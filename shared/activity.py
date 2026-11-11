#!/usr/bin/env python3
"""Run the configured RustkinsActivity clone without exposing local paths to the agent."""

import json
import subprocess
import sys
from pathlib import Path


def run(arguments, home=None):
    config_file = (home or Path.home()) / ".rustkins-skills" / "config.json"
    try:
        config = json.loads(config_file.read_text(encoding="utf-8"))
        clone_value = config.get("activity_clone") if isinstance(config, dict) else None
        if not isinstance(clone_value, str) or not clone_value:
            raise ValueError("activity_clone absent de la configuration")
        clone = Path(clone_value).expanduser().resolve(strict=True)
        if not (clone / "Cargo.toml").is_file() or not (clone / ".git").exists():
            raise ValueError("activity_clone n'est pas un clone RustkinsActivity")
        forwarded = list(arguments)
        for index, argument in enumerate(forwarded[:-1]):
            if argument == "--input":
                forwarded[index + 1] = str(Path(forwarded[index + 1]).expanduser().resolve())
        return subprocess.run(
            ["cargo", "activity", "--config", str(config_file), *forwarded],
            cwd=clone,
            check=False,
        ).returncode
    except (OSError, ValueError) as error:
        print(f"RustkinsActivity : configuration ou lancement impossible : {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
