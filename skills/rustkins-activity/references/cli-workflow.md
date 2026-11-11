# Contrat CLI pour les agents

Toutes les commandes ci-dessous s'exécutent avec `python "$HOME/.rustkins-skills/shared/activity.py"` sous PowerShell ou `python3 "$HOME/.rustkins-skills/shared/activity.py"` sous Linux avant la sous-commande, depuis n'importe quel dossier. Les chemins JSON peuvent être absolus. Le lanceur et la CLI lisent directement la configuration commune `~/.rustkins-skills/config.json` contenant `profile`, `author`, `activity_clone`, `drafts_dir`.

```text
recover
discover
prepare-create --input <fichier.json>
prepare-patch --input <fichier.json>
publish <operation_id>
validate
```

`discover` fait un `fetch origin main`, puis renvoie un JSON avec `drafts` et `activities` du profil. Chaque activité contient son `path`, son `metadata`, et ses `sections` (`text` et `sha256`). Il n'effectue **aucun rapprochement sémantique** ; l'agent tranche avant préparation. Les fiches terminales sont retournées pour contexte, jamais comme cibles de patch. Une préparation de patch relit également `origin/main` et utilise les opérations ciblées et validations du moteur Rust. La publication revalide contre la tête distante sous verrou, sans seconde recherche sémantique de doublons.

Exemple de création (l'agent adapte le contenu aux faits réels) :

```json
{
  "title": "Corriger la validation des activités",
  "agent": "codex",
  "repositories": ["Rustkins-Project/RustkinsActivity"],
  "activity_type": "bugfix",
  "status": "in_progress",
  "work_item_id": null,
  "pull_requests": [],
  "related_docs": [],
  "summary": "Corriger la validation. Fin : tests passants et PR ouverte.",
  "journal": "- Intervention commencée.",
  "blockers": "Aucun.",
  "result": "En cours."
}
```

Exemple de patch sur une fiche ouverte, en reprenant l'empreinte de `discover` :

```json
{
  "path": "activities/2026/11/Timothy/activity-<id>.md",
  "changes": [
    {"type": "append_journal", "text": "Tests exécutés : cargo test (réussi)."},
    {"type": "add_reference", "field": "pull_requests", "url": "https://github.com/Rustkins-Project/RustkinsActivity/pull/42"},
    {"type": "replace_section", "section": "Résultat et vérifications", "expected_sha256": "<sha256 de discover>", "value": "Correctif publié. cargo test réussi."},
    {"type": "set_status", "expected": "in_progress", "value": "completed", "reason": "Condition de fin satisfaite ; PR ouverte."}
  ]
}
```

Pour un passage à `blocked`, joindre `set_status` avec motif, `append_journal`, et `replace_section` de `Blocages et dépendances` indiquant l'action attendue. Pour la reprise, vérifier que le blocage est levé, puis passer de `blocked` à `in_progress`. Pour un objectif modifié, joindre `replace_section` de `Résumé` et `append_journal`. Une fiche terminale ne reçoit aucun patch ; un retour de review ultérieur crée une nouvelle activité.
