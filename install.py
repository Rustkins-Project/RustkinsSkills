#!/usr/bin/env python3
"""Install every available Rustkins skill for Codex and Claude Code."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from contextlib import ExitStack
from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parent / "skills"
SHARED_DIR = Path(__file__).resolve().parent / "shared"
PROFILES = ("Timothy", "Alexis", "Loick")
CLIENTS = (".codex", ".claude")
ACTIVITY_KEYS = ("profile", "author", "activity_clone", "drafts_dir")


def discover_skills():
    if not SKILLS_DIR.is_dir():
        raise ValueError(f"Dossier des skills introuvable : {SKILLS_DIR}")
    return sorted(
        folder for folder in SKILLS_DIR.iterdir()
        if folder.is_dir() and (folder / "SKILL.md").is_file()
    )


def requirements(skill):
    file = skill / "requirements.json"
    if not file.exists():
        return [], False
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("commands", []), list):
        raise ValueError(f"Prérequis invalides : {file}")
    commands = data.get("commands", [])
    if any(not isinstance(command, str) or not command for command in commands):
        raise ValueError(f"Commandes invalides : {file}")
    extension = data.get("azure_devops_extension", False)
    if not isinstance(extension, bool):
        raise ValueError(f"Extension Azure invalide : {file}")
    return commands, extension


def missing_requirements(skill):
    commands, extension = requirements(skill)
    missing = [command for command in commands if shutil.which(command) is None]
    if extension and "az" not in missing:
        try:
            result = subprocess.run(
                [shutil.which("az") or "az", "extension", "list", "--query", "[].name", "-o", "tsv"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                check=False,
            )
        except OSError:
            result = None
        if result is None or result.returncode != 0 or "azure-devops" not in result.stdout.splitlines():
            missing.append("az extension add --name azure-devops")
    return missing


def same_tree(source, target):
    if not target.is_dir():
        return False

    def retained_paths(root, is_dir):
        return {
            path.relative_to(root)
            for path in root.rglob("*")
            if (path.is_dir() if is_dir else path.is_file())
            and "__pycache__" not in path.relative_to(root).parts
            and path.suffix not in (".pyc", ".pyo")
        }

    source_files = retained_paths(source, is_dir=False)
    target_files = retained_paths(target, is_dir=False)
    source_dirs = retained_paths(source, is_dir=True)
    target_dirs = retained_paths(target, is_dir=True)
    return source_files == target_files and source_dirs == target_dirs and all(
        (source / relative).read_bytes() == (target / relative).read_bytes()
        for relative in source_files
    )


def activity_configuration(values, create_drafts):
    if values.get("profile") not in PROFILES:
        raise ValueError("--profile doit valoir Timothy, Alexis ou Loick")
    if not values.get("author"):
        raise ValueError("--author doit contenir le login GitHub du développeur")
    if not values.get("activity_clone") or not values.get("drafts_dir"):
        raise ValueError("--activity-clone et --drafts-dir sont requis pour rustkins-activity")
    clone = Path(values["activity_clone"]).expanduser().resolve(strict=True)
    if not (clone / "Cargo.toml").is_file() or not (clone / ".git").exists():
        raise ValueError("activity_clone doit être un clone Git de RustkinsActivity")
    drafts = Path(values["drafts_dir"]).expanduser().resolve()
    if drafts == clone or clone in drafts.parents:
        raise ValueError("drafts_dir doit être hors du clone RustkinsActivity")
    if create_drafts:
        drafts.mkdir(parents=True, exist_ok=True)
    values["activity_clone"] = str(clone)
    values["drafts_dir"] = str(drafts)
    return clone


def check_activity_cli(clone, setup):
    if setup:
        subprocess.run(["cargo", "run", "--quiet", "--", "setup"], cwd=clone, check=True)
        return
    help_text = subprocess.run(
        ["cargo", "run", "--quiet", "--", "--help"], cwd=clone,
        check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    if any(command not in help_text for command in ("discover", "prepare-create", "prepare-patch")):
        raise ValueError("La CLI RustkinsActivity doit inclure les commandes de phase 4")


def write_config_stage(config_file, values):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=config_file.parent, delete=False
    ) as stream:
        json.dump(values, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        return Path(stream.name)


def install(args):
    home = Path.home()
    config_file = home / ".rustkins-skills" / "config.json"
    previous = json.loads(config_file.read_text(encoding="utf-8")) if config_file.exists() else {}
    if not isinstance(previous, dict):
        raise ValueError(f"Configuration invalide : {config_file}")
    values = dict(previous)
    activity_values = dict(previous)
    for key in ACTIVITY_KEYS:
        value = getattr(args, key, None)
        if value is not None:
            activity_values[key] = value
    docs_clone = getattr(args, "docs_clone", None)
    if docs_clone is not None:
        values["docs_clone"] = docs_clone
    for section, key, option in (
        ("azure", "organization", "azure_organization"),
        ("azure", "project", "azure_project"),
        ("discord", "base_url", "discord_base_url"),
    ):
        value = getattr(args, option, None)
        if value is not None:
            if not isinstance(values.get(section, {}), dict):
                raise ValueError(f"Configuration invalide : {section}")
            values.setdefault(section, {})[key] = value

    skills = discover_skills()
    if not skills:
        raise ValueError(f"Aucun skill valide dans {SKILLS_DIR}")
    if not any(skill.name == "rustkins-activity" for skill in skills):
        values.update({key: activity_values[key] for key in ACTIVITY_KEYS if key in activity_values})
    available = []
    unavailable = []
    activity_clone = None
    for skill in skills:
        missing = missing_requirements(skill)
        if missing:
            unavailable.append(f"{skill.name} : prérequis absents : {', '.join(missing)}")
            continue
        if skill.name == "rustkins-activity":
            try:
                clone = activity_configuration(activity_values, create_drafts=False)
                if not getattr(args, "check", False):
                    check_activity_cli(clone, setup=False)
            except (ValueError, OSError, subprocess.CalledProcessError) as error:
                unavailable.append(f"{skill.name} : {error}")
                continue
            values.update({key: activity_values[key] for key in ACTIVITY_KEYS})
            activity_clone = clone
        available.append(skill)
    for message in unavailable:
        print(f"Skill indisponible : {message}", file=sys.stderr)
    if getattr(args, "check", False):
        for skill in available:
            print(f"Skill prêt : {skill.name}")
        return unavailable
    if not available:
        raise ValueError("Aucun skill installable ; voir les diagnostics ci-dessus")

    # Prepare every copy before replacing an installed directory.
    with ExitStack() as stack:
        replacements = []
        for client in CLIENTS:
            destination = home / client / "skills"
            destination.mkdir(parents=True, exist_ok=True)
            for skill in available:
                target = destination / skill.name
                if target.exists() and not target.is_dir():
                    raise ValueError(f"Destination occupée par un fichier : {target}")
                if same_tree(skill, target):
                    continue
                staging = Path(stack.enter_context(tempfile.TemporaryDirectory(dir=destination)))
                staged = staging / skill.name
                shutil.copytree(skill, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
                replacements.append((client, skill.name, target, staged))

        if SHARED_DIR.is_dir():
            shared_target = config_file.parent / "shared"
            if shared_target.exists() and not shared_target.is_dir():
                raise ValueError(f"Destination occupée par un fichier : {shared_target}")
            if not same_tree(SHARED_DIR, shared_target):
                config_file.parent.mkdir(parents=True, exist_ok=True)
                staging = Path(stack.enter_context(tempfile.TemporaryDirectory(dir=config_file.parent)))
                staged = staging / "shared"
                shutil.copytree(
                    SHARED_DIR, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
                )
                replacements.append(("common", "shared", shared_target, staged))

        if activity_clone is not None:
            activity_configuration(values, create_drafts=True)
            check_activity_cli(activity_clone, setup=True)

        staged_config = write_config_stage(config_file, values)
        backup_id = uuid.uuid4().hex
        backup_roots = set()
        changed = []
        try:
            for client, name, target, staged in replacements:
                backup_root = target.parent / ".rustkins-backups" / backup_id
                backup = backup_root / name if target.exists() else None
                if backup is not None:
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    target.replace(backup)
                    backup_roots.add(backup_root)
                changed.append((target, backup))
                staged.replace(target)
            staged_config.replace(config_file)
        except OSError:
            for target, backup in reversed(changed):
                if target.exists():
                    shutil.rmtree(target)
                if backup is not None and backup.exists():
                    backup.replace(target)
            raise
        finally:
            staged_config.unlink(missing_ok=True)
        for client, _, target, _ in replacements:
            label = "Ressources communes" if client == "common" else "Skill installé"
            print(f"{label} : {target}")
        for backup_root in sorted(backup_roots):
            print(f"Copies précédentes conservées : {backup_root}")
        print(f"Configuration commune : {config_file}")
    return unavailable


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--author", help="Login GitHub du responsable humain")
    parser.add_argument("--activity-clone", help="Chemin du clone RustkinsActivity")
    parser.add_argument("--drafts-dir", help="Dossier persistant hors clone")
    parser.add_argument("--docs-clone", help="Chemin du clone RustkinsDocs")
    parser.add_argument("--azure-organization", help="URL de l'organisation Azure DevOps")
    parser.add_argument("--azure-project", help="Projet Azure DevOps")
    parser.add_argument("--discord-base-url", help="URL de base du Discord Bot")
    parser.add_argument("--check", action="store_true", help="Vérifier les prérequis sans installer")
    try:
        unavailable = install(parser.parse_args())
    except (ValueError, OSError, UnicodeError, subprocess.CalledProcessError) as error:
        print(f"Installation échouée : {error}", file=sys.stderr)
        return 1
    return 1 if unavailable else 0


if __name__ == "__main__":
    raise SystemExit(main())
