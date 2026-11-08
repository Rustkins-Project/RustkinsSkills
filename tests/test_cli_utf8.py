import json
import subprocess
import tempfile
import traceback
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shared import cli_utf8


FRENCH = "Échec d'exécution — coût déjà payé, è à œ « » e\u0301 😀\nDeuxième ligne."


class CliUtf8Tests(unittest.TestCase):
    def setUp(self):
        self.which_patch = patch.object(cli_utf8.shutil, "which", side_effect=lambda name: name)
        self.which_patch.start()
        self.addCleanup(self.which_patch.stop)

    def test_windows_cmd_uses_embedded_python_without_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "wbin").mkdir()
            (root / "python.exe").touch()
            launcher = root / "wbin" / "az.CMD"
            with patch.object(cli_utf8.shutil, "which", return_value=str(launcher)):
                with patch.object(cli_utf8.subprocess, "run", return_value=SimpleNamespace(
                    returncode=0, stdout="{}", stderr=""
                )) as run:
                    cli_utf8.run_json("az", ["version", "-o", "json"])
        self.assertEqual(run.call_args.args[0][:5], [
            str(root / "python.exe"), "-X", "utf8", "-IBm", "azure.cli"
        ])
        self.assertFalse(run.call_args.kwargs["shell"])
    def test_az_json_preserves_unicode_and_uses_no_shell(self):
        payload = {"title": FRENCH, "description": "<p>É & œ</p>"}
        output = json.dumps(payload, ensure_ascii=False)
        with patch.object(cli_utf8.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout=output, stderr=""
        )) as run:
            result = cli_utf8.run_json("az", ["boards", "work-item", "show", "--id", "42"])
        self.assertEqual(result, payload)
        self.assertEqual(run.call_args.args[0], [
            "az", "boards", "work-item", "show", "--id", "42"
        ])
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
        self.assertEqual(run.call_args.kwargs["errors"], "strict")
        self.assertEqual(run.call_args.kwargs["env"]["PYTHONIOENCODING"], "utf-8")

    def test_gh_body_file_preserves_exact_multiline_utf8(self):
        with cli_utf8.temporary_markdown(FRENCH) as body_file:
            self.assertEqual(body_file.read_bytes(), FRENCH.encode("utf-8"))
            with patch.object(cli_utf8.subprocess, "run", return_value=SimpleNamespace(
                returncode=0, stdout="https://example.invalid/pr/1\n", stderr=""
            )) as run:
                cli_utf8.run_cli(
                    "gh", ["pr", "create", "--title", FRENCH, "--body-file", str(body_file)]
                )
            self.assertEqual(run.call_args.args[0][-3:], [FRENCH, "--body-file", str(body_file)])
            self.assertEqual(body_file.read_text(encoding="utf-8"), FRENCH)
        self.assertFalse(body_file.exists())

    def test_cli_arguments_preserve_accents_spaces_and_apostrophe(self):
        cwd = Path("dossier avec é")
        with patch.object(cli_utf8.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout="ok", stderr=""
        )) as run:
            self.assertEqual(cli_utf8.run_cli("gh", ["api", "nom avec é", FRENCH], cwd=cwd), "ok")
        self.assertEqual(run.call_args.args[0], ["gh", "api", "nom avec é", FRENCH])
        self.assertEqual(run.call_args.kwargs["cwd"], cwd)

    def test_failure_never_discloses_arguments_stderr_or_environment(self):
        secret = "PAT-secret-123"
        with patch.dict(cli_utf8.os.environ, {"RUSTKINS_SECRET": secret}):
            with patch.object(cli_utf8.subprocess, "run", return_value=SimpleNamespace(
                returncode=1, stdout=secret, stderr=f"Authorization: Bearer {secret}"
            )):
                with self.assertRaises(cli_utf8.CliError) as failure:
                    cli_utf8.run_cli("az", ["boards", "query", "--token", secret])
        self.assertIn("code 1", str(failure.exception))
        self.assertNotIn(secret, str(failure.exception))

    def test_timeout_diagnostic_suppresses_sensitive_command(self):
        secret = "PAT-secret-456"
        with patch.object(cli_utf8.subprocess, "run", side_effect=subprocess.TimeoutExpired(
            cmd=["gh", "api", secret], timeout=2
        )):
            with self.assertRaises(cli_utf8.CliError) as failure:
                cli_utf8.run_cli("gh", ["api", secret], timeout=2)
        rendered = "".join(traceback.format_exception(failure.exception))
        self.assertIn("délai de 2 s", rendered)
        self.assertNotIn(secret, rendered)

    def test_missing_command_invalid_utf8_and_json_are_diagnostic(self):
        with patch.object(cli_utf8.subprocess, "run", side_effect=FileNotFoundError()):
            with self.assertRaisesRegex(cli_utf8.CliError, "introuvable"):
                cli_utf8.run_cli("az", [])
        with patch.object(cli_utf8.subprocess, "run", side_effect=UnicodeDecodeError(
            "utf-8", b"\xff", 0, 1, "invalid"
        )):
            with self.assertRaisesRegex(cli_utf8.CliError, "non UTF-8"):
                cli_utf8.run_cli("gh", [])
        with patch.object(cli_utf8.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout="not json", stderr=""
        )):
            with self.assertRaisesRegex(cli_utf8.CliError, "JSON invalide"):
                cli_utf8.run_json("az", [])

    def test_utf8_json_and_markdown_files_with_unicode_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "espace et é"
            root.mkdir()
            markdown = root / "résumé.md"
            data = root / "données.json"
            cli_utf8.write_utf8(markdown, FRENCH)
            cli_utf8.write_json(data, {"title": FRENCH})
            self.assertEqual(markdown.read_bytes(), FRENCH.encode("utf-8"))
            self.assertEqual(cli_utf8.read_utf8(markdown), FRENCH)
            self.assertEqual(cli_utf8.read_json(data), {"title": FRENCH})
            self.assertIn("Échec".encode("utf-8"), data.read_bytes())
            self.assertTrue(data.read_bytes().endswith(b"\n"))

    def test_plain_text_to_html_escapes_once_and_keeps_french(self):
        value = "É <p> & \"l'exécution\"\r\nœ « déjà » 😀"
        self.assertEqual(
            cli_utf8.plain_text_to_html(value),
            "É &lt;p&gt; &amp; &quot;l&#x27;exécution&quot;<br>\nœ « déjà » 😀",
        )


if __name__ == "__main__":
    unittest.main()
