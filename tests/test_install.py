import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import install


class InstallTests(unittest.TestCase):
    def test_both_agents_share_configuration_and_update(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            clone = root / "activity"
            clone.mkdir()
            (clone / "Cargo.toml").write_text("[package]\nname='test'\n", encoding="utf-8")
            (clone / ".git").mkdir()
            args = SimpleNamespace(
                profile="Alexis",
                author="alexis-login",
                activity_clone=str(clone),
                drafts_dir=str(root / "drafts"),
            )
            with patch.object(Path, "home", return_value=home), patch.object(
                install.subprocess, "run", return_value=SimpleNamespace(
                    stdout="discover prepare-create prepare-patch"
                )
            ) as setup:
                install.install(args)
                for agent in (".codex", ".claude"):
                    skill = home / agent / "skills" / "rustkins-activity"
                    self.assertTrue((skill / "SKILL.md").is_file())
                    self.assertTrue((skill / "references" / "cli-workflow.md").is_file())
                config = (home / ".rustkins-skills" / "config.json").read_text(encoding="utf-8")
                self.assertIn('"profile": "Alexis"', config)
                self.assertIn('"author": "alexis-login"', config)
                install.install(SimpleNamespace(
                    profile=None, author=None, activity_clone=None, drafts_dir=None
                ))
                self.assertEqual(setup.call_count, 4)
                self.assertEqual(config, (home / ".rustkins-skills" / "config.json").read_text(encoding="utf-8"))

    def test_rejects_drafts_inside_clone(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clone = root / "activity"
            clone.mkdir()
            (clone / "Cargo.toml").touch()
            (clone / ".git").mkdir()
            args = SimpleNamespace(
                profile="Loick", author="loick-login", activity_clone=str(clone),
                drafts_dir=str(clone / "drafts"),
            )
            with patch.object(Path, "home", return_value=root / "home"):
                with self.assertRaisesRegex(ValueError, "hors du clone"):
                    install.install(args)


if __name__ == "__main__":
    unittest.main()
