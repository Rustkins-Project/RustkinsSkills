---
name: rustkins-docs
description: Crée, met à jour ou réorganise les documents de référence DOC et les runbooks RUN de RustkinsDocs (spécifications, architecture, conventions, versions, procédures), en appliquant les templates, les schémas et la validation documentaire jusqu'à une PR vérifiable.
---

# Rédiger des documents et runbooks Rustkins

Utilise ce skill lorsqu'on demande de **rédiger, enrichir, corriger, déplacer ou structurer un document de référence** sous `RustkinsDocs/docs/`, y compris un runbook. Lis impérativement [le parcours de rédaction et publication](references/document-workflow.md) avant toute écriture : la source de vérité est le dépôt RustkinsDocs **actuel**, pas la description mémorisée d'un schéma.

- Pour **créer ou réviser une ADR** dans `decisions/`, utilise [rustkins-adr](../rustkins-adr/SKILL.md).
- Pour une **connaissance** `KNOW` dans `knowledge/`, une recherche documentaire ou une étude exploratoire, utilise [rustkins-knowledge](../rustkins-knowledge/SKILL.md).
- Pour une décision manquante ou une contradiction qui exige l'équipe, utilise [rustkins-ask-team](../rustkins-ask-team/SKILL.md) uniquement si la consultation est autorisée.

## Parcours obligatoire

1. **Vérifie le dépôt et l'objectif.** Identifie `docs_clone` dans `~/.rustkins-skills/config.json` ou un clone vérifié de `RustkinsDocs`. Examine le remote, `main`, le worktree et les PR liées ; ne modifie jamais silencieusement une branche ou un travail local d'autrui. Pour une simple demande de brouillon sans publication, n'ouvre pas de PR de ta propre initiative si la demande ne l'implique pas.
2. **Cherche avant de créer.** Lis `INDEX.md`, le README du dossier, `docs/conventions/knowledge-management.md`, les sources de conception applicables et leurs `status`/`applies_to`. Réutilise le document canonique lorsqu'il existe. Une ADR `proposed` ou `superseded` ne démontre pas un choix actuellement applicable.
3. **Rédige depuis les sources.** Choisis le dossier et le template réel : `templates/document.md` + `schemas/document.schema.json` pour `DOC`, ou `templates/runbook.md` + `schemas/runbook.schema.json` pour `RUN` sous `docs/operations/`. Garde les faits, versions, contraintes et incertitudes exactement étayés ; n'invente ni décision ni test. Nouvel ID unique et non réservé ; un déplacement conserve l'ID historique.
4. **Relie et vérifie.** Utilise `related_docs` pour des IDs DOC/RUN existants, `related_adrs` pour des IDs ADR existants et des liens Markdown relatifs pour des fichiers. Maintiens les entrées de navigation pertinentes. Lance depuis la racine de RustkinsDocs `python scripts/validate_docs.py` (ou `python3`) ; traite les erreurs avant publication. Le contrôle historique `--base-ref` est exigé par la CI sur PR, pas par le hook local.
5. **Publie sans te substituer à la revue.** Si la demande inclut la contribution au dépôt, crée ou reprends une branche dédiée, committe, pousse, puis ouvre/actualise une PR normale via `git`/`gh`. Vérifie checks et contenu publié du corps de PR en UTF-8. Ne contourne pas la protection de `main`, n'approuve pas et ne fusionne pas la PR.

En cas de divergence entre ce skill et les conventions/schémas lus **dans la révision courante de RustkinsDocs**, signale-la et applique les règles canoniques du dépôt. Aucun nouveau service, index distant ou format inventé n'est nécessaire.
