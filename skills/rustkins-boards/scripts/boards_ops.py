#!/usr/bin/env python3
"""Conservative Azure Boards operations for Rustkins Tasks and progress states."""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote, urlparse

sys.path.insert(0, str(Path.home() / ".rustkins-skills" / "shared"))
from cli_utf8 import CliError, plain_text_to_html, read_json, run_cli, run_json, write_json


class BoardError(RuntimeError):
    """A safe diagnostic that does not include work item content or credentials."""


def configuration() -> Dict[str, str]:
    data = read_json(Path.home() / ".rustkins-skills" / "config.json")
    azure = data.get("azure") if isinstance(data, dict) else None
    if not isinstance(azure, dict):
        raise BoardError("Configuration Azure absente : renseigner --azure-organization et --azure-project")
    organization, project = azure.get("organization"), azure.get("project")
    parsed = urlparse(organization) if isinstance(organization, str) else None
    if (
        parsed is None or parsed.scheme != "https" or parsed.hostname != "dev.azure.com"
        or parsed.username or parsed.password or parsed.query or parsed.fragment
        or len(parsed.path.strip("/").split("/")) != 1
        or not parsed.path.strip("/") or not isinstance(project, str) or not project.strip()
    ):
        raise BoardError("Organisation/projet Azure invalides dans config.json")
    return {"organization": organization.rstrip("/"), "project": project}


def item(item_id: int, config: Dict[str, str]) -> Dict[str, Any]:
    result = run_json("az", [
        "boards", "work-item", "show", "--id", str(item_id),
        "--org", config["organization"], "--expand", "all", "-o", "json",
    ])
    if (
        not isinstance(result, dict) or result.get("id") != item_id
        or not isinstance(result.get("fields"), dict)
        or not isinstance(result.get("rev"), int)
    ):
        raise BoardError(f"Réponse Azure incomplète pour AB#{item_id}")
    if result["fields"].get("System.TeamProject") != config["project"]:
        raise BoardError(f"AB#{item_id} appartient à un autre projet")
    return result


def parent_id(work_item: Dict[str, Any]) -> Any:
    value = work_item["fields"].get("System.Parent")
    if isinstance(value, int):
        return value
    for relation in work_item.get("relations") or []:
        if relation.get("rel") == "System.LinkTypes.Hierarchy-Reverse":
            match = re.search(r"/workitems/(\d+)$", relation.get("url", ""), re.IGNORECASE)
            if match:
                return int(match.group(1))
    return None


def task_description(deliverable: str, done_criteria: List[str]) -> str:
    criteria = "<br>\n".join(plain_text_to_html(criterion) for criterion in done_criteria)
    return (
        f"<p><strong>Livrable :</strong> {plain_text_to_html(deliverable)}</p>"
        f"<p><strong>Critères de fin :</strong><br>\n{criteria}</p>"
    )


def same_task_description(actual: Any, expected: str) -> bool:
    """Azure may insert trailing spaces inside paragraph tags on write."""
    if not isinstance(actual, str):
        return False
    trim_paragraph_end = lambda value: re.sub(r"[ \t]+(?=</p>)", "", value)
    return trim_paragraph_end(actual) == trim_paragraph_end(expected)


def matching_tasks(parent: int, title: str, config: Dict[str, str]) -> List[Dict[str, Any]]:
    def quoted(value: str) -> str:
        return value.replace("'", "''")

    wiql = (
        "SELECT [System.Id] FROM WorkItems WHERE "
        f"[System.TeamProject] = '{quoted(config['project'])}' AND "
        "[System.WorkItemType] = 'Task' AND "
        f"[System.Title] = '{quoted(title)}'"
    )
    output = run_cli("az", [
        "boards", "query", "--wiql", wiql, "--org", config["organization"],
        "--project", config["project"], "-o", "json",
    ])
    if not output.strip():
        return []
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        raise BoardError("Résultat de recherche Azure non JSON") from None
    if result is None:
        return []
    if not isinstance(result, list):
        raise BoardError("Résultat de recherche Azure inattendu")
    matches = []
    for row in result:
        if not isinstance(row, dict) or not isinstance(row.get("id"), int):
            raise BoardError("Résultat de recherche Azure incomplet")
        candidate = item(row["id"], config)
        if candidate["fields"].get("System.WorkItemType") != "Task":
            continue
        if candidate["fields"].get("System.Title") != title:
            continue
        candidate_parent = parent_id(candidate)
        if candidate_parent == parent or candidate_parent is None:
            matches.append(candidate)
    return matches


def existing_task(parent: int, title: str, description: str, config: Dict[str, str]) -> Any:
    matches = matching_tasks(parent, title, config)
    if not matches:
        return None
    if len(matches) != 1 or parent_id(matches[0]) != parent:
        raise BoardError("Task candidate ambiguë ou sans parent ; vérifier les work items avant tout nouvel essai")
    candidate = matches[0]
    if not same_task_description(candidate["fields"].get("System.Description"), description):
        raise BoardError(f"AB#{candidate['id']} a le même titre mais un livrable différent")
    return candidate["id"]


def create_task(payload: Dict[str, Any], config: Dict[str, str]) -> int:
    if not isinstance(payload, dict):
        raise BoardError("Entrée Task invalide : objet JSON attendu")
    parent = payload.get("parent_id")
    title = payload.get("title")
    deliverable = payload.get("deliverable")
    criteria = payload.get("done_criteria")
    if (
        type(parent) is not int or parent <= 0 or not isinstance(title, str) or not title.strip()
        or not isinstance(deliverable, str) or not deliverable.strip()
        or not isinstance(criteria, list) or not criteria
        or any(not isinstance(value, str) or not value.strip() for value in criteria)
    ):
        raise BoardError("Entrée Task invalide : parent_id, title, deliverable et done_criteria sont requis")
    story = item(parent, config)
    fields = story["fields"]
    if fields.get("System.WorkItemType") != "User Story":
        raise BoardError(f"AB#{parent} n'est pas une User Story")
    if not fields.get("Microsoft.VSTS.Common.AcceptanceCriteria"):
        raise BoardError(f"AB#{parent} n'a pas de critères d'acceptation")
    if parent_id(story) is None:
        raise BoardError(f"AB#{parent} n'a pas de Feature parente vérifiée")
    iteration = fields.get("System.IterationPath")
    if not isinstance(iteration, str) or not iteration:
        raise BoardError(f"AB#{parent} n'a pas d'itération vérifiée")
    description = task_description(deliverable, criteria)
    previous = existing_task(parent, title, description, config)
    if previous is not None:
        return previous

    command = [
        "boards", "work-item", "create", "--title", title, "--type", "Task",
        "--description", description, "--iteration", iteration,
        "--org", config["organization"], "--project", config["project"], "-o", "json",
    ]
    area = fields.get("System.AreaPath")
    if isinstance(area, str) and area:
        command.extend(["--area", area])
    try:
        created = run_json("az", command)
    except CliError:
        recovered = existing_task(parent, title, description, config)
        if recovered is not None:
            return recovered
        raise BoardError("Création incertaine ; rechercher la Task et son parent avant tout nouvel essai") from None
    if not isinstance(created, dict) or not isinstance(created.get("id"), int):
        raise BoardError("Création incertaine : ID absent de la réponse Azure")
    task_id = created["id"]
    created_item = item(task_id, config)
    created_fields = created_item["fields"]
    if (
        created_fields.get("System.WorkItemType") != "Task"
        or created_fields.get("System.Title") != title
        or not same_task_description(created_fields.get("System.Description"), description)
        or created_fields.get("System.AssignedTo")
    ):
        raise BoardError(f"AB#{task_id} créé avec des champs inattendus ; vérifier avant de continuer")
    try:
        run_json("az", [
            "boards", "work-item", "relation", "add",
            "--id", str(parent), "--relation-type", "Child", "--target-id", str(task_id),
            "--org", config["organization"], "-o", "json",
        ])
    except CliError:
        if parent_id(item(task_id, config)) != parent:
            raise BoardError(f"AB#{task_id} créé mais lien parent non confirmé ; vérifier avant de réessayer") from None
    if parent_id(item(task_id, config)) != parent:
        raise BoardError(f"AB#{task_id} créé mais parent non confirmé")
    return task_id


def assignee(work_item: Dict[str, Any]) -> Any:
    value = work_item["fields"].get("System.AssignedTo")
    if isinstance(value, dict):
        return value.get("uniqueName")
    return value


def revision_patch(work_item: Dict[str, Any], field: str, value: str, config: Dict[str, str], reason: str = "") -> None:
    operations = [
        {"op": "test", "path": "/rev", "value": work_item["rev"]},
        {"op": "add", "path": f"/fields/{field}", "value": value},
    ]
    if reason:
        operations.append({"op": "add", "path": "/fields/System.History", "value": reason})
    with tempfile.TemporaryDirectory() as directory:
        body = Path(directory) / "patch.json"
        write_json(body, operations)
        url = (
            f"{config['organization']}/{quote(config['project'], safe='')}"
            f"/_apis/wit/workitems/{work_item['id']}?api-version=7.1"
        )
        run_json("az", [
            "rest", "--method", "patch", "--url", url,
            "--resource", "https://app.vssps.visualstudio.com/",
            "--headers", "Content-Type=application/json-patch+json",
            "--body", f"@{body}", "-o", "json",
        ])


def claim_task(task_id: int, identity: str, config: Dict[str, str]) -> int:
    if task_id <= 0 or not isinstance(identity, str) or not identity.strip():
        raise BoardError("ID ou identité Azure invalide")
    current = item(task_id, config)
    if current["fields"].get("System.WorkItemType") != "Task":
        raise BoardError(f"AB#{task_id} n'est pas une Task")
    assigned = assignee(current)
    if isinstance(assigned, str) and assigned.casefold() == identity.casefold():
        return task_id
    if assigned:
        raise BoardError(f"AB#{task_id} est déjà attribué ; aucune réaffectation automatique")
    try:
        revision_patch(current, "System.AssignedTo", identity, config)
    except CliError:
        latest = item(task_id, config)
        if str(assignee(latest)).casefold() != identity.casefold():
            raise BoardError(f"Attribution de AB#{task_id} non confirmée ; relire avant de réessayer") from None
    if str(assignee(item(task_id, config))).casefold() != identity.casefold():
        raise BoardError(f"Attribution de AB#{task_id} non confirmée")
    return task_id


def set_progress(task_id: int, expected: str, target: str, reason: str, config: Dict[str, str]) -> int:
    if task_id <= 0 or target not in ("Active", "Blocked", "On Hold") or not reason.strip():
        raise BoardError("Transition d'avancement invalide ou motif absent")
    current = item(task_id, config)
    work_type = current["fields"].get("System.WorkItemType")
    if work_type not in ("Task", "User Story"):
        raise BoardError("Transition d'avancement réservée aux Tasks et User Stories")
    state = current["fields"].get("System.State")
    if state != expected or expected not in ("New", "Active", "Blocked", "On Hold"):
        raise BoardError(f"État de AB#{task_id} modifié ; relire avant de réessayer")
    if state == target:
        return task_id
    try:
        revision_patch(current, "System.State", target, config, reason)
    except CliError:
        if item(task_id, config)["fields"].get("System.State") != target:
            raise BoardError(f"Transition de AB#{task_id} non confirmée ; relire avant de réessayer") from None
    if item(task_id, config)["fields"].get("System.State") != target:
        raise BoardError(f"Transition de AB#{task_id} non confirmée")
    return task_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-task")
    create.add_argument("--input", type=Path, required=True, help="JSON UTF-8 de la Task")
    claim = commands.add_parser("claim-task")
    claim.add_argument("--id", type=int, required=True)
    claim.add_argument("--identity", required=True, help="Identité Azure DevOps du développeur")
    progress = commands.add_parser("set-progress")
    progress.add_argument("--id", type=int, required=True)
    progress.add_argument("--expected", required=True)
    progress.add_argument("--to", required=True)
    progress.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        config = configuration()
        if args.command == "create-task":
            task_id = create_task(read_json(args.input), config)
        elif args.command == "claim-task":
            task_id = claim_task(args.id, args.identity, config)
        else:
            task_id = set_progress(args.id, args.expected, args.to, args.reason, config)
    except (BoardError, CliError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Opération Boards interrompue : {error}", file=sys.stderr)
        return 1
    print(json.dumps({"id": task_id, "status": "verified"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
