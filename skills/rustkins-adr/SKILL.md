---
name: rustkins-adr
description: Prépare et met à jour les Architecture Decision Records (ADR) de RustkinsDocs : recherche d'arbitrages, contexte, alternatives, conséquences, supersession et PR avec revue humaine obligatoire, sans accepter ou fusionner une décision à la place de l'équipe.
---

# Rédiger et proposer une ADR Rustkins

Utilise ce skill lorsque la demande porte sur une **décision d'architecture** ou sur la création, la révision, le rejet ou le remplacement d'un fichier sous `RustkinsDocs/decisions/`. Lis [le parcours ADR et les règles de remplacement](references/adr-workflow.md) avant de rédiger.

- Pour une spécification, une architecture descriptive, une convention ou un runbook `DOC/RUN`, utilise [rustkins-docs](../rustkins-docs/SKILL.md).
- Pour rechercher les sources, décisions et connaissances préexistantes, utilise [rustkins-knowledge](../rustkins-knowledge/SKILL.md).
- Pour poser une question non tranchée à l'équipe, sollicite [rustkins-ask-team](../rustkins-ask-team/SKILL.md) **seulement si la consultation est autorisée**.

## Parcours obligatoire

1. **Lis la source canonique.** Localise et vérifie `RustkinsDocs` (configuration `docs_clone`, remote, branche, worktree). Lis `decisions/README.md`, `docs/conventions/knowledge-management.md`, `templates/adr.md`, `schemas/adr.schema.json` et les ADR/contrats applicables dans la révision actuelle. Une rubrique « ADR » dans une ancienne architecture n'est pas automatiquement une ADR publiée.
2. **Établis le vrai arbitrage.** Formule le problème, les contraintes, les options évaluées et les conséquences vérifiables à partir des sources. Signale les points non décidés ; ne transforme jamais une discussion Discord, un brouillon ou une déduction de l'agent en approbation.
3. **Rédige une proposition.** Une nouvelle ADR utilise un ID `ADR-xxxx` unique, jamais `ADR-0000`, le template actuel, `status: proposed`, `decided_at: null`, `approved_by: []` et les H2 non vides `Contexte`, `Décision`, `Alternatives`, `Conséquences`. Distingue `applies_to` (version du produit) de la version YAML. Ne change pas une ancienne ADR acceptée pour réécrire rétroactivement sa décision.
4. **Gère un remplacement avec prudence.** Une nouvelle ADR `proposed` peut déclarer `supersedes: [ADR-....]` **sans** passer immédiatement l'ancienne ADR à `superseded`. Lorsqu'une acceptation par l'équipe doit être publiée, la transition à `accepted` et les anciens statuts à `superseded` doivent être **cohérents dans la même PR**, avec véritables `decided_at` et `approved_by`. Une ADR `superseded` reste au dépôt. Le validateur interdit les cycles.
5. **Contrôle et soumets.** Exécute `python scripts/validate_docs.py` (ou `python3`) depuis la racine RustkinsDocs, vérifie les liens/IDs et, si pertinent, le mode historique. Prépare une branche/PR via `git`/`gh`, avec preuves et résultats réellement observés. Les règles de `main` imposent une PR et une approbation humaine de `rustkins-team` pour `decisions/**` ; aucun agent ne peut approuver sa propre PR ou la merger.

**Point de gouvernance :** le statut `accepted` n'est opposable qu'après une décision humaine, la revue requise et la fusion sur `main`. Une PR de nouvelle ADR encore `proposed`, même mergée, reste une **proposition** ; ne la présente jamais comme acceptée. La CI vérifie le schéma et le graphe, **pas** le consentement humain.
