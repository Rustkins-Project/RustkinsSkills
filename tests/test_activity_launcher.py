import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from shared import activity


class ActivityLauncherTests(unittest.TestCase):
    def test_uses_configured_clone_and_passes_config_to_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            config = home / ".rustkins-skills" / "config.json"
            config.parent.mkdir(parents=True)
            clone = Path(directory) / "clone avec espaces"
            clone.mkdir()
            (clone / "Cargo.toml").touch()
            (clone / ".git").mkdir()
            config.write_text(json.dumps({"activity_clone": str(clone)}), encoding="utf-8")

            with patch.object(activity.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as execute:
                self.assertEqual(activity.run(["discover"], home), 0)

            execute.assert_called_once_with(
                ["cargo", "activity", "--config", str(config), "discover"],
                cwd=clone,
                check=False,
            )

            with patch.object(activity.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as execute:
                self.assertEqual(activity.run(["prepare-create", "--input", "payload.json"], home), 0)
            execute.assert_called_once_with(
                ["cargo", "activity", "--config", str(config), "prepare-create", "--input",
                 str(Path("payload.json").resolve())],
                cwd=clone,
                check=False,
            )

    def test_missing_configuration_fails_without_starting_cargo(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(activity.subprocess, "run") as execute:
                self.assertEqual(activity.run(["discover"], Path(directory)), 1)
                execute.assert_not_called()
