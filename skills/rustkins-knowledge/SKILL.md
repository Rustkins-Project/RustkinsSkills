---
name: rustkins-knowledge
description: Recherche les décisions, spécifications et connaissances Rustkins dans RustkinsDocs avec leur statut et leur version, puis prépare une contribution documentaire ou une ADR proposée par PR sans dupliquer ni approuver une décision.
---

# Connaissance et décisions Rustkins

Utilise ce skill pour répondre depuis RustkinsDocs à une question de conception, documenter une solution durable ou proposer une ADR. Lis [la recherche et les niveaux d'autorité](references/search.md) pour une lecture ; lis aussi [la contribution documentaire](references/contribute.md) avant toute écriture. Le dépôt RustkinsDocs est la source de vérité des documents, Azure Boards celle du backlog et RustkinsActivity celle des interventions.

## Rechercher

1. Identifie le sujet, le composant et la version **du produit**. Trouve le clone RustkinsDocs configuré dans `~/.rustkins-skills/config.json` (`docs_clone`) ou un clone local vérifié. Vérifie son dépôt, son remote, sa branche et son worktree avant toute synchronisation.
2. Commence par `INDEX.md`, puis cherche dans les spécifications, l'architecture et `decisions/` ; consulte `knowledge/` et `research/` si nécessaire. Cherche par mots métier, variantes techniques et version, puis lis les fichiers pertinents et leur frontmatter. Une rubrique historique intitulée « ADR » dans une page d'architecture n'est pas une ADR acceptée dans `decisions/`.
3. Pour chaque conclusion, donne le chemin, la révision consultée, `status`, `applies_to` et les limites utiles. Une ADR `proposed` ou `superseded`, une note `candidate` et une recherche ne sont pas des règles validées. Si deux sources officielles applicables se contredisent, signale les deux et fais arbitrer via `rustkins-ask-team` lorsque cette consultation est autorisée.

## Contribuer

4. Avant de créer, recherche un document équivalent, ses liens et son identifiant. Choisis le type et le dossier selon RustkinsDocs : ADR dans `decisions/`, note réutilisable dans `knowledge/`, contrat dans `docs/specifications/`, conception dans `docs/architecture/`, procédure dans `docs/operations/`. Enrichis l'existant quand il couvre déjà le sujet.
5. Travaille dans une branche ou un worktree d'écriture distinct, sur une base à jour. Pars du template et du schéma du dépôt ; préserve l'ID stable, `status`, `applies_to`, les preuves et les liens. Une ADR nouvelle ou supersédante reste `proposed` avec `approved_by: []` et `decided_at: null` ; une connaissance sans preuve reste `candidate`.
6. Vérifie frontmatter, IDs, liens relatifs, index et références modifiés ; exécute les contrôles disponibles sans déclarer un succès non mesuré. Committe, pousse et ouvre une PR normale avec un corps Markdown UTF-8 vérifié. Une ADR exige l'approbation d'un **autre humain** avant fusion ; aucune ADR n'est acceptée ou fusionnée par l'agent. Les autres PR documentaires restent soumises au workflow humain du dépôt.

Une réponse Discord validée peut servir de référence pour une proposition, mais ne devient pas une ADR acceptée. Ne publie ni conversation complète, ni secret, ni donnée privée inutile. Si une Task ou US officielle est en jeu, utilise `rustkins-boards` pour son suivi plutôt que de recopier le backlog dans RustkinsDocs.
