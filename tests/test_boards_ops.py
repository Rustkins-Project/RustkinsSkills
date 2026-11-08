import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared"))
SPEC = importlib.util.spec_from_file_location(
    "boards_ops", ROOT / "skills" / "rustkins-boards" / "scripts" / "boards_ops.py"
)
boards = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boards)

CONFIG = {"organization": "https://dev.azure.com/rustkins", "project": "Rustkins"}
PAYLOAD = {
    "parent_id": 142,
    "title": "Valider l'exécution — É 🚀",
    "deliverable": "Afficher <ok> & l'erreur\nÉchec",
    "done_criteria": ["« résultat » vérifié", "Tests passés"],
}


def work_item(item_id, kind, title="", parent=None, assigned=None, state="New", description=None, rev=3):
    fields = {
        "System.TeamProject": "Rustkins",
        "System.WorkItemType": kind,
        "System.Title": title,
        "System.State": state,
        "System.AssignedTo": assigned,
        "System.IterationPath": "Rustkins\\Sprint 1",
        "System.AreaPath": "Rustkins",
        "Microsoft.VSTS.Common.AcceptanceCriteria": "<p>OK</p>",
    }
    if parent is not None:
        fields["System.Parent"] = parent
    if description is not None:
        fields["System.Description"] = description
    return {"id": item_id, "rev": rev, "fields": fields, "relations": []}


class BoardsTests(unittest.TestCase):
    def test_configuration_rejects_cross_host_and_missing_project(self):
        with patch.object(boards, "read_json", return_value={"azure": {
            "organization": "https://evil.example/rustkins", "project": "Rustkins"
        }}):
            with self.assertRaises(boards.BoardError):
                boards.configuration()
        with patch.object(boards, "read_json", return_value={"azure": {
            "organization": "https://dev.azure.com/rustkins", "project": ""
        }}):
            with self.assertRaises(boards.BoardError):
                boards.configuration()

    def test_description_escapes_html_without_losing_french(self):
        result = boards.task_description(PAYLOAD["deliverable"], PAYLOAD["done_criteria"])
        self.assertIn("&lt;ok&gt; &amp; l&#x27;erreur<br>\nÉchec", result)
        self.assertIn("« résultat » vérifié", result)

    def test_matching_tasks_escapes_wiql_and_follows_parent(self):
        other = work_item(2, "Task", PAYLOAD["title"], parent=999)
        matching = work_item(3, "Task", PAYLOAD["title"], parent=142)
        def fake_run(tool, args):
            self.assertIn("l''exécution", args[3])
            return json.dumps([{"id": 2}, {"id": 3}])
        with patch.object(boards, "run_cli", side_effect=fake_run), patch.object(
            boards, "item", side_effect=[other, matching]
        ):
            self.assertEqual([3], [x["id"] for x in boards.matching_tasks(142, PAYLOAD["title"], CONFIG)])

    def test_empty_successful_query_has_no_candidates(self):
        with patch.object(boards, "run_cli", return_value=""):
            self.assertEqual([], boards.matching_tasks(142, "Titre nouveau", CONFIG))
        with patch.object(boards, "run_cli", return_value="null\n"):
            self.assertEqual([], boards.matching_tasks(142, "Titre nouveau", CONFIG))

    def test_failed_or_invalid_query_does_not_become_no_candidates(self):
        with patch.object(boards, "run_cli", side_effect=boards.CliError("az failed")):
            with self.assertRaises(boards.CliError):
                boards.matching_tasks(142, "Titre nouveau", CONFIG)
        with patch.object(boards, "run_cli", return_value="unexpected output"):
            with self.assertRaises(boards.BoardError):
                boards.matching_tasks(142, "Titre nouveau", CONFIG)

    def test_reuses_exact_existing_task_without_creating(self):
        story = work_item(142, "User Story", "US", parent=40)
        description = boards.task_description(PAYLOAD["deliverable"], PAYLOAD["done_criteria"])
        task = work_item(151, "Task", PAYLOAD["title"], parent=142, description=description)
        with patch.object(boards, "item", return_value=story), patch.object(
            boards, "matching_tasks", return_value=[task]
        ), patch.object(boards, "run_json") as run:
            self.assertEqual(151, boards.create_task(PAYLOAD, CONFIG))
            run.assert_not_called()

    def test_azure_paragraph_spacing_is_accepted_without_ignoring_content(self):
        expected = boards.task_description(PAYLOAD["deliverable"], PAYLOAD["done_criteria"])
        actual = expected.replace("</p>", " </p>")
        self.assertTrue(boards.same_task_description(actual, expected))
        self.assertFalse(boards.same_task_description(actual.replace("Tests passés", "Tests ratés"), expected))

    def test_rejects_unparented_duplicate(self):
        story = work_item(142, "User Story", "US", parent=40)
        task = work_item(151, "Task", PAYLOAD["title"], description=boards.task_description(
            PAYLOAD["deliverable"], PAYLOAD["done_criteria"]
        ))
        with patch.object(boards, "item", return_value=story), patch.object(
            boards, "matching_tasks", return_value=[task]
        ):
            with self.assertRaises(boards.BoardError):
                boards.create_task(PAYLOAD, CONFIG)

    def test_uncertain_create_does_not_retry(self):
        story = work_item(142, "User Story", "US", parent=40)
        with patch.object(boards, "item", return_value=story), patch.object(
            boards, "matching_tasks", return_value=[]
        ) as matching, patch.object(
            boards, "run_json", side_effect=boards.CliError("timeout")
        ) as run:
            with self.assertRaisesRegex(boards.BoardError, "incertaine"):
                boards.create_task(PAYLOAD, CONFIG)
            self.assertEqual(2, matching.call_count)
            self.assertEqual(1, run.call_count)

    def test_rejects_non_object_payload(self):
        with self.assertRaises(boards.BoardError):
            boards.create_task([PAYLOAD], CONFIG)

    def test_creates_unassigned_task_then_confirms_parent(self):
        story = work_item(142, "User Story", "US", parent=40)
        description = boards.task_description(PAYLOAD["deliverable"], PAYLOAD["done_criteria"])
        unlinked = work_item(151, "Task", PAYLOAD["title"], description=description)
        linked = work_item(151, "Task", PAYLOAD["title"], parent=142, description=description)
        calls = []
        def fake_run(tool, args):
            calls.append(args)
            if args[:3] == ["boards", "work-item", "create"]:
                self.assertNotIn("--assigned-to", args)
                return {"id": 151}
            return {"id": 151}
        with patch.object(boards, "item", side_effect=[story, unlinked, linked]), patch.object(
            boards, "matching_tasks", return_value=[]
        ), patch.object(boards, "run_json", side_effect=fake_run):
            self.assertEqual(151, boards.create_task(PAYLOAD, CONFIG))
        self.assertEqual(2, len(calls))
        self.assertIn("--relation-type", calls[1])

    def test_claim_never_overwrites_another_assignee(self):
        assigned = work_item(151, "Task", assigned={"uniqueName": "other@example.org"})
        with patch.object(boards, "item", return_value=assigned), patch.object(
            boards, "revision_patch"
        ) as mutate:
            with self.assertRaises(boards.BoardError):
                boards.claim_task(151, "me@example.org", CONFIG)
            mutate.assert_not_called()

    def test_claim_uses_revision_patch_and_verifies(self):
        empty = work_item(151, "Task")
        claimed = work_item(151, "Task", assigned={"uniqueName": "me@example.org"}, rev=4)
        with patch.object(boards, "item", side_effect=[empty, claimed]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            self.assertEqual(151, boards.claim_task(151, "me@example.org", CONFIG))
            mutate.assert_called_once_with(empty, "System.AssignedTo", "me@example.org", CONFIG)

    def test_claim_after_lost_response_requires_confirmed_identity(self):
        empty = work_item(151, "Task")
        claimed = work_item(151, "Task", assigned={"uniqueName": "me@example.org"}, rev=4)
        with patch.object(boards, "item", side_effect=[empty, claimed, claimed]), patch.object(
            boards, "revision_patch", side_effect=boards.CliError("timeout")
        ):
            self.assertEqual(151, boards.claim_task(151, "me@example.org", CONFIG))

    def test_progress_requires_expected_state_and_records_reason(self):
        active = work_item(151, "Task", state="Active")
        blocked = work_item(151, "Task", state="Blocked", rev=4)
        with patch.object(boards, "item", side_effect=[active, blocked]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            boards.set_progress(151, "Active", "Blocked", "Dépend de AB#9", CONFIG)
            mutate.assert_called_once_with(active, "System.State", "Blocked", CONFIG, "Dépend de AB#9")
        with patch.object(boards, "item", return_value=active):
            with self.assertRaises(boards.BoardError):
                boards.set_progress(151, "New", "Blocked", "Dépendance", CONFIG)

    def test_iteration_move_checks_story_and_previous_path(self):
        story = work_item(142, "User Story")
        moved = work_item(142, "User Story", rev=4)
        moved["fields"]["System.IterationPath"] = "Rustkins\\Sprint 2"
        with patch.object(boards, "item", side_effect=[story, moved]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            self.assertEqual(142, boards.set_iteration(
                142, "Rustkins\\Sprint 1", "Rustkins\\Sprint 2", "Planning validé", CONFIG
            ))
            mutate.assert_called_once_with(
                story, "System.IterationPath", "Rustkins\\Sprint 2", CONFIG, "Planning validé"
            )
        with patch.object(boards, "item", return_value=story), patch.object(
            boards, "revision_patch"
        ) as mutate:
            with self.assertRaises(boards.BoardError):
                boards.set_iteration(142, "Rustkins\\Autre", "Rustkins\\Sprint 2", "Décision", CONFIG)
            with self.assertRaises(boards.BoardError):
                boards.set_iteration(142, "Rustkins\\Sprint 1", "Autre\\Sprint 2", "Décision", CONFIG)
            mutate.assert_not_called()
        resolved = work_item(142, "User Story", state="Resolved")
        with patch.object(boards, "item", return_value=resolved), patch.object(
            boards, "revision_patch"
        ) as mutate:
            with self.assertRaises(boards.BoardError):
                boards.set_iteration(142, "Rustkins\\Sprint 1", "Rustkins\\Sprint 2", "Report", CONFIG)
            mutate.assert_not_called()

    def test_carryover_moves_only_approved_unfinished_child_task(self):
        task = work_item(151, "Task", parent=142, state="Active")
        story = work_item(142, "User Story", state="Active")
        story["fields"]["System.IterationPath"] = "Rustkins\\Sprint 2"
        moved = work_item(151, "Task", parent=142, state="Active", rev=4)
        moved["fields"]["System.IterationPath"] = "Rustkins\\Sprint 2"
        with patch.object(boards, "item", side_effect=[task, story, moved]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            self.assertEqual(151, boards.set_task_iteration(
                151, 142, "Rustkins\\Sprint 1", "Rustkins\\Sprint 2", "Report validé", CONFIG
            ))
            mutate.assert_called_once_with(
                task, "System.IterationPath", "Rustkins\\Sprint 2", CONFIG, "Report validé"
            )
        for bad_task in (work_item(151, "Task", parent=142, state="Closed"),
                         work_item(151, "Task", parent=999, state="Active")):
            with patch.object(boards, "item", return_value=bad_task), patch.object(
                boards, "revision_patch"
            ) as mutate:
                with self.assertRaises(boards.BoardError):
                    boards.set_task_iteration(
                        151, 142, "Rustkins\\Sprint 1", "Rustkins\\Sprint 2", "Report", CONFIG
                    )
                mutate.assert_not_called()
        story["fields"]["System.IterationPath"] = "Rustkins\\Sprint 1"
        with patch.object(boards, "item", side_effect=[task, story]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            with self.assertRaisesRegex(boards.BoardError, "sprint cible"):
                boards.set_task_iteration(
                    151, 142, "Rustkins\\Sprint 1", "Rustkins\\Sprint 2", "Report", CONFIG
                )
            mutate.assert_not_called()
    def test_review_acceptance_requires_resolved_story_and_closed_tasks(self):
        decision = {
            "story_id": 142, "expected_revision": 3,
            "decision": "accepted", "sprint": "Rustkins\\Sprint 1",
            "review_date": "2026-11-08", "participants": ["Timothy", "Alexis"],
            "review_url": "https://github.com/Rustkins-Project/RustkinsDocs/pull/7",
            "reason": "AC démontrés sur la plateforme de test",
        }
        story = work_item(142, "User Story", state="Resolved")
        story["relations"] = [{
            "rel": "System.LinkTypes.Hierarchy-Forward",
            "url": "https://dev.azure.com/rustkins/_apis/wit/workItems/151",
        }]
        task = work_item(151, "Task", parent=142, state="Closed")
        closed = work_item(142, "User Story", state="Closed", rev=4)
        with patch.object(boards, "item", side_effect=[story, task, closed]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            self.assertEqual(142, boards.review_story(decision, CONFIG))
            self.assertEqual(mutate.call_args.args[:4], (story, "System.State", "Closed", CONFIG))
            self.assertIn("Sprint Review 2026-11-08", mutate.call_args.args[4])
            self.assertIn(decision["review_url"], mutate.call_args.args[4])
        task["fields"]["System.State"] = "Active"
        with patch.object(boards, "item", side_effect=[story, task]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            with self.assertRaisesRegex(boards.BoardError, "non Closed"):
                boards.review_story(decision, CONFIG)
            mutate.assert_not_called()
        with patch.object(boards, "item", return_value=story), patch.object(
            boards, "revision_patch"
        ) as mutate:
            with self.assertRaisesRegex(boards.BoardError, "relire"):
                boards.review_story({**decision, "expected_revision": 2}, CONFIG)
            mutate.assert_not_called()

    def test_review_rejection_returns_story_to_active_and_validates_decision(self):
        decision = {
            "story_id": 142, "expected_revision": 3,
            "decision": "rejected", "sprint": "Rustkins\\Sprint 1",
            "review_date": "2026-11-08", "participants": ["Loick"],
            "review_url": "https://github.com/Rustkins-Project/RustkinsDocs/pull/7",
            "reason": "AC initial non satisfait",
        }
        resolved = work_item(142, "User Story", state="Resolved")
        active = work_item(142, "User Story", state="Active", rev=4)
        with patch.object(boards, "item", side_effect=[resolved, active]), patch.object(
            boards, "revision_patch"
        ) as mutate:
            self.assertEqual(142, boards.review_story(decision, CONFIG))
            self.assertEqual(mutate.call_args.args[2], "Active")
        for bad in ({**decision, "review_date": "20261108"}, {**decision, "participants": []},
                    {**decision, "review_url": "http://example.org"},
                    {**decision, "review_url": "https://github.com/other/repo/pull/7"}):
            with patch.object(boards, "item") as read:
                with self.assertRaises(boards.BoardError):
                    boards.review_story(bad, CONFIG)
                read.assert_not_called()

    def test_patch_body_checks_revision(self):
        current = work_item(151, "Task", rev=7)
        captured = []
        def fake_run(tool, args):
            body = Path(args[args.index("--body") + 1][1:])
            captured.extend(json.loads(body.read_text(encoding="utf-8")))
            self.assertEqual(args[:3], ["rest", "--method", "patch"])
            self.assertEqual(args[args.index("--url") + 1],
                             "https://dev.azure.com/rustkins/Rustkins/_apis/wit/workitems/151?api-version=7.1")
            self.assertIn("https://app.vssps.visualstudio.com/", args)
            self.assertIn("Content-Type=application/json-patch+json", args)
            return {"id": 151}
        with patch.object(boards, "run_json", side_effect=fake_run):
            boards.revision_patch(current, "System.State", "Blocked", CONFIG, "Échec d'exécution")
        self.assertEqual({"op": "test", "path": "/rev", "value": 7}, captured[0])
        self.assertEqual("/fields/System.History", captured[2]["path"])
        self.assertEqual("Échec d'exécution", captured[2]["value"])


if __name__ == "__main__":
    unittest.main()
