# Sprint Review, rétrospective et report

Vérifie l'Iteration Path dans Azure, puis collecte les US `Resolved` et les US non terminées avec `rustkins-sprint-status`. Relis chaque US et ses Tasks via `rustkins-boards`, les AC et les preuves de DoD. Seule une décision de l'équipe pendant la review autorise `Closed` ; une US `Resolved` sans décision reste `Resolved`.

Dans `RustkinsDocs`, crée deux fichiers sous `docs/project-management/sprints/<sprint>/` :

- `review.md` : sprint, date, participants, Sprint Goal, démonstrations, AC et preuves, décision acceptée/refusée par ID d'US, remarques, Bugs/évolutions, report et actions.
- `retrospective.md` : sprint, date, participants, points positifs, difficultés, décisions et quelques actions avec responsable et critère de vérification au sprint suivant.

Lis le schéma et les conventions documentaires de RustkinsDocs avant d'écrire le frontmatter ; garde un ID unique et un statut honnête. Les rapports sont publiés par PR revuable et fusion humaine. Le lien de cette PR ou du document sur `main` sert de `review_url` dans la décision Azure. Préserve la différence entre une décision prise en réunion et une PR documentaire encore ouverte.

Après la décision humaine, prépare un fichier JSON UTF-8 hors dépôt :

```json
{
  "story_id": 142,
  "expected_revision": 3,
  "decision": "accepted",
  "sprint": "Rustkins\\Sprint 1",
  "review_date": "2026-11-08",
  "participants": ["Timothy", "Alexis", "Loick"],
  "review_url": "https://github.com/Rustkins-Project/RustkinsDocs/pull/7",
  "reason": "AC et DoD démontrés sur la plateforme de test"
}
```

`decision` vaut `accepted` (transition `Resolved → Closed`) ou `rejected` (transition `Resolved → Active`, avec AC initial manqué dans `reason`). Les valeurs sont illustratives, jamais une décision réelle. `expected_revision` est la révision Azure examinée pendant la review : si elle a changé, réévalue la décision avec l'équipe avant une nouvelle tentative. Le `review_url` pointe vers la PR ou le document de compte rendu dans RustkinsDocs. Exécute `python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" review-story --input <fichier.json>` (ou le chemin frère `.claude`), puis relis l'US et son historique. Après un timeout ou un rejet, relis l'état et la révision avant tout nouvel essai. Le script vérifie le type, l'itération, l'état, les AC, les Tasks enfants et la révision ; il ne peut pas juger la qualité de la démonstration ou la présence effective des participants.

Pour les US reportées, Timothy valide la nouvelle itération et l'impact avant `set-iteration --id <id> --expected '<ancien sprint>' --to '<nouveau sprint>' --reason '<décision>'`. Une US `Resolved` non acceptée ne se déplace pas sans décision explicite sur son état. Les Tasks déjà `Closed` restent en place. Note séparément SP engagés, SP livrés par les US `Closed`, et SP non livrés.
