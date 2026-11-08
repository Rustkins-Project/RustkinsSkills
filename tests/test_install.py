import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import install


def args(**overrides):
    values = dict(
        profile=None, author=None, activity_clone=None, drafts_dir=None,
        docs_clone=None, azure_organization=None, azure_project=None,
        discord_base_url=None, check=False,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def make_skill(root, name, content="---\nname: sample\n---\n"):
    folder = root / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(content, encoding="utf-8")
    return folder


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.skills = self.root / "skills"
        self.skills.mkdir()
        self.shared = self.root / "shared"
        self.home_patch = patch.object(Path, "home", return_value=self.home)
        self.skills_patch = patch.object(install, "SKILLS_DIR", self.skills)
        self.shared_patch = patch.object(install, "SHARED_DIR", self.shared)
        self.which_patch = patch.object(install.shutil, "which", return_value="tool")
        self.home_patch.start()
        self.skills_patch.start()
        self.shared_patch.start()
        self.which_patch.start()
        self.addCleanup(self.home_patch.stop)
        self.addCleanup(self.skills_patch.stop)
        self.addCleanup(self.shared_patch.stop)
        self.addCleanup(self.which_patch.stop)

    def config(self):
        return json.loads((self.home / ".rustkins-skills" / "config.json").read_text(encoding="utf-8"))

    def target(self, client, name):
        return self.home / client / "skills" / name

    def test_discovery_full_resources_unicode_and_new_settings(self):
        one = make_skill(self.skills, "rustkins-boards", "É è à É œ « » l'exécution 😀\n")
        (one / "references").mkdir()
        (one / "references" / "étapes.md").write_text("Échec — « déjà »\n", encoding="utf-8")
        (one / "scripts").mkdir()
        (one / "scripts" / "outil.py").write_text("print('à')\n", encoding="utf-8")
        make_skill(self.skills, "rustkins-work")
        (self.skills / "not-a-skill").mkdir()
        install.install(args(
            docs_clone=str(self.root / "Docs français"),
            azure_organization="https://dev.azure.com/équipe",
            azure_project="Projet É",
            discord_base_url="https://bot.example.invalid",
        ))
        for client in install.CLIENTS:
            for name in ("rustkins-boards", "rustkins-work"):
                self.assertTrue((self.target(client, name) / "SKILL.md").is_file())
            self.assertFalse(self.target(client, "not-a-skill").exists())
            self.assertEqual(
                (self.target(client, "rustkins-boards") / "references" / "étapes.md").read_text(encoding="utf-8"),
                "Échec — « déjà »\n",
            )
            self.assertTrue((self.target(client, "rustkins-boards") / "scripts" / "outil.py").is_file())
        self.assertEqual(self.config()["azure"]["project"], "Projet É")
        self.assertEqual(self.config()["docs_clone"], str(self.root / "Docs français"))

    def test_activity_compatibility_rerun_update_and_backup(self):
        skill = make_skill(self.skills, "rustkins-activity", "ancien\n")
        (skill / "requirements.json").write_text('{"commands": ["git", "cargo"]}', encoding="utf-8")
        (skill / "references").mkdir()
        (skill / "references" / "cli.md").write_text("référence\n", encoding="utf-8")
        clone = self.root / "clone avec é espaces"
        clone.mkdir()
        (clone / "Cargo.toml").write_text("[package]\n", encoding="utf-8")
        (clone / ".git").mkdir()
        drafts = self.root / "brouillons é"
        with patch.object(install.subprocess, "run", return_value=SimpleNamespace(
            stdout="discover prepare-create prepare-patch"
        )) as run:
            self.assertEqual(install.install(args(
                profile="Alexis", author="l'auteur-é", activity_clone=str(clone), drafts_dir=str(drafts)
            )), [])
            self.assertTrue(drafts.is_dir())
            self.assertEqual(self.config()["author"], "l'auteur-é")
            first = self.target(".codex", "rustkins-activity")
            self.assertTrue((first / "references" / "cli.md").is_file())
            install.install(args())
            self.assertFalse((self.home / ".codex" / "skills" / ".rustkins-backups").exists())
            (skill / "SKILL.md").write_text("nouveau\n", encoding="utf-8")
            install.install(args())
            self.assertEqual((first / "SKILL.md").read_text(encoding="utf-8"), "nouveau\n")
            backups = list((self.home / ".codex" / "skills" / ".rustkins-backups").glob(
                "*/rustkins-activity/SKILL.md"
            ))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "ancien\n")
            self.assertEqual(run.call_count, 6)
            self.assertEqual(self.config()["activity_clone"], str(clone))

    def test_preserves_existing_configuration_and_local_installed_files(self):
        skill = make_skill(self.skills, "rustkins-work", "new\n")
        config_file = self.home / ".rustkins-skills" / "config.json"
        config_file.parent.mkdir(parents=True)
        config_file.write_text(json.dumps({
            "profile": "Timothy", "author": "ancien", "custom": {"clé": "É"},
            "azure": {"organization": "https://old", "extra": "gardé"},
        }, ensure_ascii=False), encoding="utf-8")
        target = self.target(".codex", skill.name)
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("local\n", encoding="utf-8")
        (target / "notes privées.md").write_text("à garder\n", encoding="utf-8")
        install.install(args(azure_organization="https://new"))
        config = self.config()
        self.assertEqual(config["profile"], "Timothy")
        self.assertEqual(config["custom"], {"clé": "É"})
        self.assertEqual(config["azure"], {"organization": "https://new", "extra": "gardé"})
        backups = list((self.home / ".codex" / "skills" / ".rustkins-backups").glob(
            "*/rustkins-work/notes privées.md"
        ))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "à garder\n")

    def test_invalid_activity_override_does_not_replace_previous_settings(self):
        make_skill(self.skills, "rustkins-activity")
        make_skill(self.skills, "rustkins-work")
        clone = self.root / "valid-activity"
        clone.mkdir()
        (clone / "Cargo.toml").touch()
        (clone / ".git").mkdir()
        config_file = self.home / ".rustkins-skills" / "config.json"
        config_file.parent.mkdir(parents=True)
        previous = {
            "profile": "Timothy", "author": "original",
            "activity_clone": str(clone), "drafts_dir": str(self.root / "drafts"),
        }
        config_file.write_text(json.dumps(previous), encoding="utf-8")
        installed_activity = self.target(".codex", "rustkins-activity")
        installed_activity.mkdir(parents=True)
        (installed_activity / "SKILL.md").write_text("existing\n", encoding="utf-8")
        missing = install.install(args(
            author="rejected", activity_clone=str(self.root / "missing-clone")
        ))
        self.assertIn("rustkins-activity", missing[0])
        self.assertEqual(self.config(), previous)
        self.assertEqual((installed_activity / "SKILL.md").read_text(encoding="utf-8"), "existing\n")
        self.assertTrue((self.target(".claude", "rustkins-work") / "SKILL.md").is_file())

    def test_optional_requirements_do_not_block_other_skills(self):
        make_skill(self.skills, "free")
        needs = make_skill(self.skills, "needs-az")
        (needs / "requirements.json").write_text(
            '{"commands": ["az"], "azure_devops_extension": true}', encoding="utf-8"
        )
        with patch.object(install.shutil, "which", side_effect=lambda name: None if name == "az" else "tool"):
            missing = install.install(args())
        self.assertIn("needs-az", missing[0])
        self.assertTrue((self.target(".codex", "free") / "SKILL.md").exists())
        self.assertFalse(self.target(".claude", "needs-az").exists())

    def test_new_skill_is_found_on_later_run(self):
        make_skill(self.skills, "first")
        install.install(args())
        make_skill(self.skills, "later")
        install.install(args())
        for client in install.CLIENTS:
            self.assertTrue((self.target(client, "later") / "SKILL.md").exists())
            self.assertTrue((self.target(client, "first") / "SKILL.md").exists())
        self.assertFalse((self.home / ".codex" / "skills" / ".rustkins-backups").exists())

    def test_shared_helpers_are_installed_and_updated_with_backup(self):
        make_skill(self.skills, "free")
        self.shared.mkdir()
        (self.shared / "cli_utf8.py").write_text("ancien\n", encoding="utf-8")
        install.install(args())
        installed = self.home / ".rustkins-skills" / "shared" / "cli_utf8.py"
        self.assertEqual(installed.read_text(encoding="utf-8"), "ancien\n")
        install.install(args())
        self.assertFalse((self.home / ".rustkins-skills" / ".rustkins-backups").exists())
        (self.shared / "cli_utf8.py").write_text("nouveau\n", encoding="utf-8")
        install.install(args())
        self.assertEqual(installed.read_text(encoding="utf-8"), "nouveau\n")
        backups = list((self.home / ".rustkins-skills" / ".rustkins-backups").glob(
            "*/shared/cli_utf8.py"
        ))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "ancien\n")

    def test_python_caches_are_not_installed_or_treated_as_source_changes(self):
        make_skill(self.skills, "free")
        self.shared.mkdir()
        (self.shared / "cli_utf8.py").write_text("code\n", encoding="utf-8")
        (self.shared / "__pycache__").mkdir()
        (self.shared / "__pycache__" / "cli_utf8.pyc").write_bytes(b"cache")
        install.install(args())
        target = self.home / ".rustkins-skills" / "shared"
        self.assertFalse((target / "__pycache__").exists())
        (target / "__pycache__").mkdir()
        (target / "__pycache__" / "cli_utf8.pyc").write_bytes(b"runtime-cache")
        install.install(args())
        self.assertFalse((self.home / ".rustkins-skills" / ".rustkins-backups").exists())

    def test_installed_shared_module_can_be_imported(self):
        make_skill(self.skills, "free")
        source = Path(install.__file__).resolve().parent / "shared"
        with patch.object(install, "SHARED_DIR", source):
            install.install(args())
        path = self.home / ".rustkins-skills" / "shared" / "cli_utf8.py"
        spec = importlib.util.spec_from_file_location("installed_cli_utf8", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.plain_text_to_html("É & œ"), "É &amp; œ")

    def test_backup_rename_stays_on_destination_filesystem(self):
        make_skill(self.skills, "one", "updated\n")
        targets = []
        for client in install.CLIENTS:
            target = self.target(client, "one")
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("previous\n", encoding="utf-8")
            targets.append(target)
        original_replace = Path.replace

        def reject_cross_device_backup(path, destination):
            if path in targets and path.parent not in Path(destination).parents:
                raise OSError(18, "Invalid cross-device link")
            return original_replace(path, destination)

        with patch.object(Path, "replace", reject_cross_device_backup):
            install.install(args())
        for target in targets:
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "updated\n")
            backups = list((target.parent / ".rustkins-backups").glob("*/one/SKILL.md"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "previous\n")

    def test_azure_extension_is_checked_only_when_declared(self):
        make_skill(self.skills, "free")
        needs = make_skill(self.skills, "needs-az")
        (needs / "requirements.json").write_text(
            '{"commands": ["az"], "azure_devops_extension": true}', encoding="utf-8"
        )
        with patch.object(install.shutil, "which", side_effect=lambda name: (
            r"C:\Program Files\Azure CLI\az.CMD" if name == "az" else "tool"
        )):
            with patch.object(install.subprocess, "run", return_value=SimpleNamespace(
                returncode=0, stdout="azure-devops\n"
            )) as run:
                self.assertEqual(install.install(args(check=True)), [])
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][:3], [
            r"C:\Program Files\Azure CLI\az.CMD", "extension", "list"
        ])
        self.assertFalse(self.home.exists())

    def test_check_is_read_only(self):
        make_skill(self.skills, "free")
        self.assertEqual(install.install(args(check=True)), [])
        self.assertFalse(self.home.exists())

    def test_copy_failure_preserves_previous_install_and_config(self):
        make_skill(self.skills, "one", "updated\n")
        target = self.target(".codex", "one")
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("previous\n", encoding="utf-8")
        with patch.object(install.shutil, "copytree", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                install.install(args())
        self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "previous\n")
        self.assertFalse((self.home / ".rustkins-skills" / "config.json").exists())

    def test_swap_failure_restores_both_clients_and_configuration(self):
        make_skill(self.skills, "one", "updated\n")
        for client in install.CLIENTS:
            target = self.target(client, "one")
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("previous\n", encoding="utf-8")
        config_file = self.home / ".rustkins-skills" / "config.json"
        config_file.parent.mkdir(parents=True)
        config_file.write_text('{"author": "previous"}\n', encoding="utf-8")
        original_replace = Path.replace
        failed = False

        def fail_second_swap(path, target):
            nonlocal failed
            if not failed and str(target).endswith(str(Path(".claude") / "skills" / "one")):
                failed = True
                raise OSError("swap failed")
            return original_replace(path, target)

        with patch.object(Path, "replace", fail_second_swap):
            with self.assertRaisesRegex(OSError, "swap failed"):
                install.install(args(author="new"))
        for client in install.CLIENTS:
            self.assertEqual((self.target(client, "one") / "SKILL.md").read_text(encoding="utf-8"), "previous\n")
        self.assertEqual(config_file.read_text(encoding="utf-8"), '{"author": "previous"}\n')

    def test_config_write_failure_restores_skills_and_shared_helpers(self):
        make_skill(self.skills, "one", "updated\n")
        self.shared.mkdir()
        (self.shared / "cli_utf8.py").write_text("updated\n", encoding="utf-8")
        targets = [self.target(client, "one") for client in install.CLIENTS]
        targets.append(self.home / ".rustkins-skills" / "shared")
        for target in targets:
            target.mkdir(parents=True)
            filename = "cli_utf8.py" if target.name == "shared" else "SKILL.md"
            (target / filename).write_text("previous\n", encoding="utf-8")
        config_file = self.home / ".rustkins-skills" / "config.json"
        config_file.write_text('{"author": "previous"}\n', encoding="utf-8")
        original_replace = Path.replace
        failed = False

        def fail_config_write(path, destination):
            nonlocal failed
            if not failed and destination == config_file:
                failed = True
                raise OSError("config failed")
            return original_replace(path, destination)

        with patch.object(Path, "replace", fail_config_write):
            with self.assertRaisesRegex(OSError, "config failed"):
                install.install(args(author="new"))
        for target in targets:
            filename = "cli_utf8.py" if target.name == "shared" else "SKILL.md"
            self.assertEqual((target / filename).read_text(encoding="utf-8"), "previous\n")
        self.assertEqual(config_file.read_text(encoding="utf-8"), '{"author": "previous"}\n')

    def test_rejects_drafts_inside_clone_without_writing(self):
        make_skill(self.skills, "rustkins-activity")
        clone = self.root / "activity"
        clone.mkdir()
        (clone / "Cargo.toml").touch()
        (clone / ".git").mkdir()
        with patch.object(install.subprocess, "run") as run:
            missing = install.install(args(
                profile="Loick", author="loick-login", activity_clone=str(clone),
                drafts_dir=str(clone / "drafts"), check=True,
            ))
        self.assertIn("hors du clone", missing[0])
        self.assertFalse((clone / "drafts").exists())
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
