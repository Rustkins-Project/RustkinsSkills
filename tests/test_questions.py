import importlib.util
import json
import tempfile
import unittest
import urllib.error
import uuid
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "rustkins-ask-team" / "scripts" / "questions.py"
spec = importlib.util.spec_from_file_location("rustkins_questions", SCRIPT)
questions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(questions)


class Reply:
    def __init__(self, status, body):
        self.status = status
        self.body = json.dumps(body, ensure_ascii=False).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit):
        return self.body


class Api:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, *, timeout):
        self.requests.append(request)
        assert timeout == 15
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        config = self.home / ".rustkins-skills" / "config.json"
        config.parent.mkdir()
        config.write_text(json.dumps({"profile": "Timothy", "discord": {"base_url": "https://bot.example.test"}}), encoding="utf-8")
        self.input = self.home / "question.json"
        self.content = {
            "title": "Échec d’exécution — coût déjà payé",
            "question": "Valide-t-on l’arrêt gracieux ? 🦀",
            "context": "Deux options : « attendre » ou terminer.\nAB#142",
            "references": [{"label": "PR", "url": "https://github.com/Rustkins-Project/example/pull/4"}],
        }
        self.input.write_text(json.dumps(self.content, ensure_ascii=False), encoding="utf-8")
        self.token = patch.dict("os.environ", {questions.TOKEN_ENV: "secret-token"})
        self.token.start()
        self.addCleanup(self.token.stop)

    def response(self, question_id, status="pending", answer=None):
        return {
            "question_id": question_id,
            "status": status,
            "publication_status": "published",
            "discord_thread_url": "https://discord.com/channels/1/2",
            "answer": answer,
        }

    def test_prepare_timeout_retry_get_pending_then_answered(self):
        first = questions.prepare(self.home, self.input)
        self.assertEqual(first, questions.prepare(self.home, self.input))
        state = questions.state_path(self.home, questions.fingerprint(self.content)).read_text(encoding="utf-8")
        self.assertNotIn("Échec", state)
        self.assertNotIn("secret-token", state)
        self.assertIsNone(first["question_id"])

        question_id = str(uuid.uuid4())
        api = Api(TimeoutError(), Reply(202, self.response(question_id)), Reply(200, self.response(question_id)))
        with self.assertRaisesRegex(questions.QuestionError, "même question préparée"):
            questions.submit(self.home, self.input, opener=api)
        self.assertEqual(questions.submit(self.home, self.input, opener=api)["question_id"], question_id)
        self.assertEqual(questions.submit(self.home, self.input, opener=api)["status"], "pending")
        first_payload = json.loads(api.requests[0].data.decode("utf-8"))
        second_payload = json.loads(api.requests[1].data.decode("utf-8"))
        self.assertEqual(first_payload, second_payload)
        self.assertEqual(first_payload["idempotency_key"], first["idempotency_key"])
        self.assertEqual(first_payload["title"], self.content["title"])
        self.assertEqual(api.requests[2].get_method(), "GET")
        self.assertEqual(questions.list_questions(self.home)[0]["question_id"], question_id)

        answer = {
            "content": "Décision validée : arrêt gracieux.",
            "discord_message_url": "https://discord.com/channels/1/2/3",
            "answered_by_discord_id": "4",
            "validated_by_discord_id": "5",
            "validated_at": "2026-11-08T18:00:00Z",
        }
        api = Api(Reply(200, self.response(question_id, "answered", answer)))
        self.assertEqual(questions.get_question(self.home, question_id, opener=api)["answer"], answer)

    def test_rejects_changed_payload_without_new_preparation(self):
        questions.prepare(self.home, self.input)
        self.content["question"] = "Autre question"
        self.input.write_text(json.dumps(self.content, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(questions.QuestionError, "non préparée"):
            questions.submit(self.home, self.input, opener=Api())

    def test_separates_state_by_human_profile(self):
        first = questions.prepare(self.home, self.input)
        config = self.home / ".rustkins-skills" / "config.json"
        config.write_text(json.dumps({"profile": "Alexis", "discord": {"base_url": "https://bot.example.test"}}), encoding="utf-8")
        second = questions.prepare(self.home, self.input)
        self.assertNotEqual(first["idempotency_key"], second["idempotency_key"])
        self.assertEqual(len(questions.list_questions(self.home)), 1)

    def test_auth_error_never_exposes_token_or_response(self):
        questions.prepare(self.home, self.input)
        error = urllib.error.HTTPError("https://bot.example.test", 401, "private response", {}, None)
        with self.assertRaises(questions.QuestionError) as caught:
            questions.submit(self.home, self.input, opener=Api(error))
        self.assertNotIn("secret-token", str(caught.exception))
        self.assertNotIn("private response", str(caught.exception))
        self.assertIn("HTTP 401", str(caught.exception))

    def test_https_and_input_validation_prevent_bad_requests(self):
        self.content["references"][0]["url"] = "http://not-secure.test"
        self.input.write_text(json.dumps(self.content), encoding="utf-8")
        with self.assertRaisesRegex(questions.QuestionError, "HTTPS"):
            questions.prepare(self.home, self.input)
        self.content["references"] = []
        self.input.write_text(json.dumps(self.content), encoding="utf-8")
        questions.prepare(self.home, self.input)
        config = self.home / ".rustkins-skills" / "config.json"
        config.write_text(json.dumps({"profile": "Timothy", "discord": {"base_url": "http://bot.example.test"}}), encoding="utf-8")
        with self.assertRaisesRegex(questions.QuestionError, "HTTPS"):
            questions.submit(self.home, self.input, opener=Api())

    def test_answered_status_requires_validated_answer_object(self):
        question_id = str(uuid.uuid4())
        api = Api(Reply(200, self.response(question_id, "answered")))
        with self.assertRaisesRegex(questions.QuestionError, "Réponse validée ou provenance absente"):
            questions.get_question(self.home, question_id, opener=api)


if __name__ == "__main__":
    unittest.main()
