# Spécification — rustkins-knowledge

> **Statut :** implémenté au jalon 6 dans [`skills/rustkins-knowledge/`](../../skills/rustkins-knowledge/SKILL.md). La recherche de source approuvée a été vérifiée pendant la recette intégrée ; une contribution documentaire par PR est préparée dans le cadre de l'alignement global des guides. Aucune proposition d'ADR réelle n'a encore été exercée. Source canonique : [conventions RustkinsDocs](https://github.com/Rustkins-Project/RustkinsDocs/blob/main/docs/conventions/knowledge-management.md).

## Objectifs

Pour une rédaction spécialisée de `DOC/RUN`, voir [rustkins-docs](rustkins-docs.md) ; pour une ADR, voir [rustkins-adr](rustkins-adr.md). `rustkins-knowledge` conserve la recherche et la production de notes `KNOW`.

Rechercher et lire la documentation utile avant toute décision de conception ; contribuer à RustkinsDocs sans créer des doublons ; proposer ADR, connaissances, spécifications ou runbooks par PR lorsque c'est pertinent. Ne pas remplacer la recherche par des suppositions ni attribuer au MCP la fonction de moteur de recherche.

## Entrées et usages

- « Quelle ADR concerne les ressources du Scheduler ? » : recherche locale ciblée et réponse avec fichiers + statut + commit/contexte.
- « Documente cette solution vérifiée » : rechercher une note existante, l'enrichir ou proposer un nouveau `knowledge/`.
- « Propose une ADR sur le cache » : consulter décisions existantes, marquer la proposition et préparer une PR, sans acceptation automatique.
- « Reprends la décision Discord » : lire seulement la réponse **validée**, créer la proposition documentaire appropriée.

## Lecture et recherche

1. Identifier le projet/version concernée et les mots clés métier/techniques.
2. Utiliser un clone local de lecture `RustkinsDocs`, synchronisé par `git pull --ff-only` **uniquement si son worktree est propre** ; ne jamais écraser des modifications locales ou modifier un worktree de travail.
3. Rechercher d'abord les références autoritatives pertinentes : `INDEX.md`, `docs/specifications/`, `docs/architecture/`, `decisions/`, puis `knowledge/` et `research/` si nécessaire.
4. Lire les fichiers nécessaires, pas toutes les archives. Prendre en compte frontmatter, statut, `applies_to`, date et décision supersédée.
5. Présenter la provenance (chemin, ref/commit si disponible, statut). Un document `draft` ou une connaissance `candidate` n'est pas une décision validée.
6. En cas de contradiction entre documents approuvés, signaler le conflit et demander un arbitrage via `rustkins-ask-team` plutôt que choisir arbitrairement.

L'implémentation peut commencer avec `git grep`, recherche par fichiers et métadonnées ; **aucun index sémantique distant obligatoire**. Les lectures à distance utilisent `gh` quand nécessaire.

## Contribution documentaire

- Vérifier le **type** (ADR, connaissance durable, spécification, procédure, convention), le bon chemin et les templates/schémas de RustkinsDocs.
- Rechercher si un document équivalent existe avant création ; préserver les liens et IDs stables.
- **ADR** : proposition `proposed`, revue humaine par au moins **un autre membre** puis merge ; aucune ADR `accepted` par décision de l'agent ; changement d'une ADR acceptée via nouvelle décision supersédante lorsque pertinent.
- **Connaissance** : `candidate` si non vérifiée, `verified` seulement avec preuves ; la gouvernance ne rend pas la revue humaine obligatoire pour les notes de connaissance, mais la PR reste recommandée pour traçabilité.
- **Autres documents structurants** : PR, tests des liens et schémas, revue selon impact.
- Ne jamais reproduire une conversation complète, des secrets, des PAT ou des messages privés ; publier uniquement les conclusions utiles et références vérifiables.
- Une réponse validée par Discord peut appuyer un brouillon d'ADR ; elle ne vaut pas acceptation dans GitHub/RustkinsDocs.

## PR et outil

Brancher en local via Git, modifier les Markdown UTF-8 avec leurs frontmatters existants, tester la syntaxe/IDs/liens, ouvrir la PR avec `gh`. Le workflow d'une PR documentaire suit les mêmes limites humaines de review/merge que `rustkins-work`.

La recherche/production documentaire ne crée pas automatiquement un work item Azure. Si la demande est une Task/US avec suivi officiel, utiliser `rustkins-boards`.

## Recette

- Retrouver ADR acceptée vs supersédée et n'en citer qu'une selon la version concernée.
- Reprendre une connaissance existante plutôt que dupliquer ; créer une connaissance candidate si la preuve manque.
- Proposer une ADR en PR sans la marquer acceptée ni l'auto-merger.
- Lors de changements de chemins, vérifier les liens Markdown et l'index.
- UTF-8 intact dans les frontmatters et les contenus en français.
