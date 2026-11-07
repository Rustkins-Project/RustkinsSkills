#!/usr/bin/env python3
"""Install or refresh the same RustkinsActivity skill for Codex and Claude Code."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL = Path(__file__).resolve().parent / "skills" / "rustkins-activity"
PROFILES = ("Timothy", "Alexis", "Loick")


def install(args: argparse.Namespace) -> None:
    home = Path.home()
    config_file = home / ".rustkins-skills" / "config.json"
    previous = json.loads(config_file.read_text(encoding="utf-8")) if config_file.exists() else {}
    values = {
        "profile": args.profile or previous.get("profile"),
        "author": args.author or previous.get("author"),
        "activity_clone": args.activity_clone or previous.get("activity_clone"),
        "drafts_dir": args.drafts_dir or previous.get("drafts_dir"),
    }
    if values["profile"] not in PROFILES:
        raise ValueError("--profile doit valoir Timothy, Alexis ou Loick")
    if not values["author"]:
        raise ValueError("--author doit contenir le login GitHub du développeur")
    if not values["activity_clone"] or not values["drafts_dir"]:
        raise ValueError("--activity-clone et --drafts-dir sont requis à la première installation")

    clone = Path(values["activity_clone"]).expanduser().resolve(strict=True)
    if not (clone / "Cargo.toml").is_file() or not (clone / ".git").exists():
        raise ValueError("activity_clone doit être un clone Git de RustkinsActivity")
    drafts = Path(values["drafts_dir"]).expanduser().resolve()
    if drafts == clone or clone in drafts.parents:
        raise ValueError("drafts_dir doit être hors du clone RustkinsActivity")
    drafts.mkdir(parents=True, exist_ok=True)
    values["activity_clone"] = str(clone)
    values["drafts_dir"] = str(drafts)

    help_text = subprocess.run(
        ["cargo", "run", "--quiet", "--", "--help"],
        cwd=clone,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if any(command not in help_text for command in ("discover", "prepare-create", "prepare-patch")):
        raise ValueError("La CLI RustkinsActivity doit inclure les commandes de phase 4")

    # Setup checks existing hooks rather than replacing them blindly.
    subprocess.run(
        ["cargo", "run", "--quiet", "--", "setup"],
        cwd=clone,
        check=True,
    )

    for destination in (home / ".codex" / "skills", home / ".claude" / "skills"):
        destination.mkdir(parents=True, exist_ok=True)
        target = destination / SKILL.name
        with tempfile.TemporaryDirectory(dir=destination) as staging_dir:
            staged = Path(staging_dir) / SKILL.name
            shutil.copytree(SKILL, staged)
            backup = Path(staging_dir) / "previous"
            if target.exists():
                if not target.is_dir():
                    raise ValueError(f"Destination occupée par un fichier : {target}")
                target.replace(backup)
            try:
                staged.replace(target)
            except OSError:
                if backup.exists():
                    backup.replace(target)
                raise
        print(f"Skill installé : {target}")

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=config_file.parent, delete=False
    ) as staged_config:
        json.dump(values, staged_config, ensure_ascii=False, indent=2)
        staged_config.write("\n")
        staged_path = Path(staged_config.name)
    staged_path.replace(config_file)
    print(f"Configuration commune : {config_file}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--author", help="Login GitHub du responsable humain")
    parser.add_argument("--activity-clone", help="Chemin du clone RustkinsActivity")
    parser.add_argument("--drafts-dir", help="Dossier persistant hors clone")
    args = parser.parse_args()
    try:
        install(args)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Installation échouée : {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
