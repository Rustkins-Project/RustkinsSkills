# Rechercher dans RustkinsDocs

La convention canonique est `docs/conventions/knowledge-management.md` dans RustkinsDocs. Lis-la lorsque l'autorité, le classement ou le statut est incertain. `INDEX.md` donne les chemins d'entrée ; le frontmatter de chaque fichier donne son ID, son statut et son `applies_to`. La version YAML d'une spécification de pipeline n'est pas la version du produit.

## Choisir et synchroniser le clone

Prends `docs_clone` dans `~/.rustkins-skills/config.json` si défini ; sinon cherche un clone local RustkinsDocs et vérifie son remote. Si aucun clone n'est disponible, lis les fichiers nécessaires sur GitHub avec `gh` et indique la révision consultée. Ne suppose pas qu'un chemin nommé « Docs » est le bon dépôt.

Dans un clone sur `main` et **propre**, `git pull --ff-only` peut mettre la lecture à jour. Si le worktree est modifié ou sur une branche de contribution, ne lance pas ce pull. Tu peux lire une révision déjà connue avec `git show 'origin/main:INDEX.md'` ou, après un `git fetch origin main` sûr pour le worktree, chercher dans la référence distante avec `git grep -n -i -e <terme> origin/main -- docs/ decisions/ knowledge/`. Ne décris pas le worktree local comme la version officielle tant que son écart avec `origin/main` n'est pas vérifié. Note le SHA via `git rev-parse origin/main` ou celui de la révision réellement lue.

## Ordre de lecture

1. `INDEX.md` et les README de navigation utiles.
2. `docs/specifications/` pour les contrats et `docs/architecture/` pour la conception applicable ; `docs/conventions/` et `docs/project-management/` pour leurs règles propres.
3. `decisions/` pour les ADR, avec `status`, `applies_to`, `supersedes` et l'état sur `main` ; vérifie l'approbation de la PR si le caractère accepté n'est pas établi.
4. `knowledge/` pour les observations vérifiées, puis `research/` pour les pistes exploratoires.

Utilise `rg --files` pour localiser, puis `rg -n -i -e <terme> <dossier>` ou `git grep` pour réduire les candidats. Lis les fichiers eux-mêmes et les renvois indispensables ; un résultat de recherche seul ne prouve ni le statut ni l'applicabilité. Vérifie si une décision plus récente supersède la première et si une page d'architecture ne contient qu'une proposition historique. Les sections « ADR-001 » incluses dans les anciens fichiers d'architecture ne sont pas des fichiers ADR gouvernés sous `decisions/`.

Pour répondre, cite le chemin relatif dans RustkinsDocs, le SHA ou la branche consultée, le statut et la version du produit. Sépare faits approuvés, connaissances vérifiées et hypothèses. Un document `draft`, une ADR `proposed` ou `superseded`, une connaissance `candidate` ou `outdated` et une recherche ne doivent pas être présentés comme une décision actuelle. En cas de contradiction entre sources applicables et approuvées, expose le conflit et demande un arbitrage ; [rustkins-ask-team](../../rustkins-ask-team/SKILL.md) traite la question et sa réponse validée.
