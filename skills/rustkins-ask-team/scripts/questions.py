"""Durable, minimal client for RustkinsDiscordBot's private questions API."""

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path


TOKEN_ENV = "RUSTKINS_DISCORD_AI_TOKEN"
MAX_RESPONSE_BYTES = 1_000_000


class QuestionError(Exception):
    """A diagnostic safe to show without response bodies or credentials."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise QuestionError(f"Fichier JSON illisible : {path.name}") from None


def request_content(path):
    data = read_json(path)
    if not isinstance(data, dict) or set(data) != {"title", "question", "context", "references"}:
        raise QuestionError("La question doit contenir title, question, context et references uniquement")
    for field, maximum in (("title", 150), ("question", 4000), ("context", 2000)):
        value = data[field]
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise QuestionError(f"Champ {field} vide ou trop long (maximum {maximum})")
    references = data["references"]
    if not isinstance(references, list) or len(references) > 10:
        raise QuestionError("references doit être une liste de dix liens au maximum")
    for reference in references:
        if not isinstance(reference, dict) or set(reference) != {"label", "url"}:
            raise QuestionError("Chaque référence doit contenir label et url uniquement")
        label, url = reference["label"], reference["url"]
        if not isinstance(label, str) or not label.strip() or len(label) > 100:
            raise QuestionError("Label de référence vide ou trop long")
        if not isinstance(url, str) or len(url) > 500 or not valid_https_url(url):
            raise QuestionError("Chaque référence exige une URL HTTPS absolue")
    return data


def valid_https_url(value):
    try:
        if any(ord(character) < 33 for character in value):
            return False
        parsed = urllib.parse.urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def fingerprint(content):
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def state_directory(home):
    config = read_json(home / ".rustkins-skills" / "config.json")
    profile = config.get("profile") if isinstance(config, dict) else None
    if profile not in ("Timothy", "Alexis", "Loick"):
        raise QuestionError("Profil humain absent de ~/.rustkins-skills/config.json")
    return home / ".rustkins-skills" / "ask-team" / profile / "questions"


def state_path(home, digest):
    return state_directory(home) / f"{digest}.json"


def save_state(path, state, *, create=False):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    temporary = path.with_name(f".{path.stem}.{uuid.uuid4()}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            os.chmod(temporary, 0o600)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if create:
            try:
                os.link(temporary, path)
            except FileExistsError:
                return False
            return True
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_state(path):
    state = read_json(path)
    if not isinstance(state, dict) or state.get("fingerprint") != path.stem:
        raise QuestionError("État local invalide ; aucune nouvelle question ne sera créée")
    try:
        uuid.UUID(state["idempotency_key"])
        if state.get("question_id") is not None:
            uuid.UUID(state["question_id"])
    except (KeyError, TypeError, ValueError):
        raise QuestionError("Identifiant local invalide ; aucune nouvelle question ne sera créée") from None
    return state


def prepare(home, input_file):
    content = request_content(input_file)
    digest = fingerprint(content)
    path = state_path(home, digest)
    state = {
        "fingerprint": digest,
        "idempotency_key": str(uuid.uuid4()),
        "question_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if not save_state(path, state, create=True):
        state = load_state(path)
    return {"idempotency_key": state["idempotency_key"], "question_id": state["question_id"]}


def settings(home):
    config = read_json(home / ".rustkins-skills" / "config.json")
    discord = config.get("discord") if isinstance(config, dict) else None
    base = discord.get("base_url") if isinstance(discord, dict) else None
    if not isinstance(base, str) or not valid_https_url(base):
        raise QuestionError("Configurer discord.base_url avec une URL HTTPS dans ~/.rustkins-skills/config.json")
    parsed = urllib.parse.urlsplit(base)
    if parsed.query or parsed.fragment:
        raise QuestionError("discord.base_url ne doit contenir ni query ni fragment")
    token = os.environ.get(TOKEN_ENV)
    if not token or not token.strip() or "\r" in token or "\n" in token:
        raise QuestionError(f"Définir {TOKEN_ENV} avec le jeton client IA du développeur")
    return base.rstrip("/"), token


def api_request(method, url, token, *, payload=None, expected_status, opener=None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    open_request = opener or urllib.request.build_opener(NoRedirect).open
    try:
        with open_request(request, timeout=15) as response:
            status = response.status
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        code = error.code
        if code in (401, 403):
            reason = "accès refusé ; vérifier le jeton et l'auteur"
        elif code == 404:
            reason = "question introuvable ou non accessible à cet auteur"
        elif code == 409:
            reason = "clé d'idempotence déjà utilisée avec un autre contenu"
        elif code == 429:
            reason = "limite de débit ; reprendre plus tard avec la même question préparée"
        elif code >= 500:
            reason = "service indisponible ; reprendre avec la même question préparée"
        elif code in (301, 302, 303, 307, 308):
            reason = "redirection refusée pour protéger le jeton"
        else:
            reason = "requête refusée ; vérifier les champs transmis"
        raise QuestionError(f"HTTP {code} : {reason}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise QuestionError("Réseau ou délai dépassé ; reprendre avec la même question préparée") from None
    if status != expected_status:
        raise QuestionError(f"HTTP {status} inattendu ; vérifier l'état avant de réessayer")
    if len(raw) > MAX_RESPONSE_BYTES:
        raise QuestionError("Réponse trop volumineuse")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        raise QuestionError("Réponse JSON UTF-8 invalide") from None
    if not isinstance(result, dict):
        raise QuestionError("Réponse JSON inattendue")
    try:
        uuid.UUID(result["question_id"])
    except (KeyError, TypeError, ValueError):
        raise QuestionError("Réponse sans question_id valide") from None
    if result.get("status") not in ("pending", "answered"):
        raise QuestionError("Statut de question inconnu")
    if result["status"] == "answered":
        answer = result.get("answer")
        if (
            not isinstance(answer, dict)
            or not isinstance(answer.get("content"), str)
            or not answer["content"].strip()
            or not isinstance(answer.get("discord_message_url"), str)
            or not valid_https_url(answer["discord_message_url"])
        ):
            raise QuestionError("Réponse validée ou provenance absente")
    return result


def submit(home, input_file, *, opener=None):
    content = request_content(input_file)
    path = state_path(home, fingerprint(content))
    if not path.is_file():
        raise QuestionError("Question non préparée ; lancer prepare avec le même fichier avant submit")
    state = load_state(path)
    base, token = settings(home)
    if state["question_id"]:
        return get_question(home, state["question_id"], opener=opener)
    payload = {"idempotency_key": state["idempotency_key"], **content}
    result = api_request("POST", base + "/internal/questions", token, payload=payload, expected_status=202, opener=opener)
    state["question_id"] = result["question_id"]
    save_state(path, state)
    return result


def get_question(home, question_id, *, opener=None):
    try:
        question_id = str(uuid.UUID(question_id))
    except (TypeError, ValueError):
        raise QuestionError("question_id doit être un UUID") from None
    base, token = settings(home)
    return api_request("GET", base + "/internal/questions/" + question_id, token, expected_status=200, opener=opener)


def list_questions(home):
    result = []
    for path in sorted(state_directory(home).glob("*.json")):
        state = load_state(path)
        result.append({"fingerprint": state["fingerprint"], "idempotency_key": state["idempotency_key"], "question_id": state["question_id"], "created_at": state.get("created_at")})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "submit"):
        command = commands.add_parser(name)
        command.add_argument("--input", type=Path, required=True, help="Fichier JSON UTF-8 de la question")
    command = commands.add_parser("get")
    command.add_argument("--question-id", required=True)
    commands.add_parser("list")
    args = parser.parse_args(argv)
    home = Path.home()
    try:
        if args.command == "prepare":
            result = prepare(home, args.input)
        elif args.command == "submit":
            result = submit(home, args.input)
        elif args.command == "get":
            result = get_question(home, args.question_id)
        else:
            result = list_questions(home)
    except QuestionError as error:
        print(str(error), file=sys.stderr)
        return 1
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
