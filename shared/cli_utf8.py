"""Small UTF-8 helpers for future Rustkins skills using az and gh."""

import html
import json
import os
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Literal, Optional, Sequence


Tool = Literal["az", "gh"]


class CliError(RuntimeError):
    """A safe diagnostic that never includes arguments, output, or environment."""


def run_cli(
    tool: Tool,
    args: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    timeout: float = 30,
) -> str:
    """Run az or gh without a shell and return UTF-8 stdout on success."""
    if tool not in ("az", "gh"):
        raise ValueError("Outil non pris en charge")
    if not isinstance(args, (list, tuple)) or any(not isinstance(arg, str) for arg in args):
        raise ValueError("Les arguments doivent être une liste de chaînes")
    if timeout <= 0:
        raise ValueError("Le délai doit être positif")

    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            [tool, *args],
            cwd=cwd,
            env=environment,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        raise CliError(f"{tool} introuvable ; installez l'outil et vérifiez PATH") from None
    except subprocess.TimeoutExpired:
        raise CliError(f"{tool} : délai de {timeout:g} s dépassé ; vérifiez l'état distant avant un nouvel essai") from None
    except UnicodeError:
        raise CliError(f"{tool} : sortie non UTF-8") from None
    except OSError:
        raise CliError(f"{tool} : lancement impossible") from None
    if result.returncode != 0:
        raise CliError(f"{tool} : échec (code {result.returncode}) ; vérifiez l'état distant avant un nouvel essai")
    return result.stdout


def run_json(
    tool: Tool,
    args: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    timeout: float = 30,
) -> Any:
    """Parse structured CLI output without logging its possibly sensitive content."""
    output = run_cli(tool, args, cwd=cwd, timeout=timeout)
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        raise CliError(f"{tool} : sortie JSON invalide") from None


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_utf8(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def read_json(path: Path) -> Any:
    return json.loads(read_utf8(path))


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def plain_text_to_html(text: str) -> str:
    """Escape plain text for an HTML field, preserving Unicode and line breaks."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return html.escape(normalized, quote=True).replace("\n", "<br>\n")


@contextmanager
def temporary_markdown(text: str) -> Iterator[Path]:
    """Provide a closed UTF-8 file for commands such as gh --body-file."""
    path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", suffix=".md", delete=False
        ) as stream:
            path = Path(stream.name)
            stream.write(text)
        yield path
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
