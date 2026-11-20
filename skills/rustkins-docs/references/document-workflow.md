# Rédaction et publication d'un document RustkinsDocs

Ce guide est une **procédure agent**, pas une copie définitive de la politique. Avant toute mutation, lire dans le clone ou la révision GitHub pertinente de RustkinsDocs : `INDEX.md`, `docs/conventions/knowledge-management.md`, le README de destination, les templates et les schémas exacts. La validation effective appartient à `scripts/validate_docs.py`.

## 1. Choisir la bonne forme

| Besoin | Emplacement | Template et schéma | ID et statut prudent |
| --- | --- | --- | --- |
| Architecture et interactions techniques | `docs/architecture/**` | `templates/document.md`, `schemas/document.schema.json` | `DOC-xxxx`, `draft` |
| Contrat ou comportement attendu | `docs/specifications/**` | Document | `DOC-xxxx`, `draft` |
| Conventions, projet, versions, thèmes transversaux | `docs/conventions/**`, `docs/project-management/**`, `docs/versions/**`, `docs/cross-cutting/**` | Document | `DOC-xxxx`, `draft` |
| Procédure opérationnelle | `docs/operations/**` | `templates/runbook.md`, `schemas/runbook.schema.json` | `RUN-xxxx`, `draft`, `type: operation` |
| Décision de conception | `decisions/**` | Voir `rustkins-adr` | `ADR-xxxx`, `proposed` |
| Solution réutilisable / observation | `knowledge/**` | Voir `rustkins-knowledge` | `KNOW-xxxx`, `candidate` |
| Exploration sans valeur normative | `research/**` | Ne pas faire passer pour une spécification | Pas d'ID imposé par le validateur |

**Tous** les `README.md` sous ces dossiers et les `README.md`/`INDEX.md` racine sont des pages de navigation, sans frontmatter obligatoire. Évite de créer un nouveau README pour y stocker un contrat officiel ; donne-lui un nom dédié.

La version **du produit** dans `applies_to` est `V0`, `V1`, `V2`, `V3` ou `all` seul ; la **version de syntaxe YAML** reste distincte (`specification_version` si le schéma l'autorise). Ne multiplie pas les fichiers par version sans différences réelles de contrat. Le type du frontmatter doit correspondre au dossier, notamment `architecture`, `specification`, `convention`, `project-management`, `version` ou `cross-cutting`.

## 2. Déterminer la source et l'identité

1. Identifie la demande, ses faits établis, les décisions encore ouvertes et les versions applicables. Recherche par sujet, synonymes, ID et versions dans les spécifications et ADR acceptées avant de t'appuyer sur une connaissance candidate ou une recherche exploratoire. Renvoie à `rustkins-knowledge` pour le parcours de recherche détaillé.
2. Vérifie si le contenu doit **modifier** un document existant plutôt qu'en créer un autre. Garde alors **exactement son ID**, même si le fichier change de chemin ; ne supprime pas un DOC/RUN publié et n'attribue pas son ID à un autre sujet.
3. Pour une création, relève les IDs effectivement utilisés dans `main`, dans le worktree candidat et dans les PR ouvertes susceptibles d'entrer en conflit ; choisis un identifiant inédit d'au moins quatre chiffres. Les IDs `DOC-0000` et `RUN-0000` sont réservés aux templates. Le choix par « plus grand numéro + 1 » est une **proposition**, jamais une réservation atomique : relis le registre avant de pousser puis laisse la CI du commit de fusion résoudre les collisions concurrentes.
4. S'il manque des éléments essentiels pour affirmer un comportement, conserve des questions/limites explicites dans le brouillon plutôt que d'inventer des spécifications, tests, approbations ou dates.

## 3. Écrire un document utile

- Pars d'une **copie du template courant**, pas d'un frontmatter recréé de mémoire. Renseigne les champs requis : `id`, `title`, `type`, `status`, `summary`, `topics`, `applies_to`. Lis le schéma pour les champs optionnels autorisés ; aucun champ arbitraire.
- `summary` court et factuel (maximum de 500 caractères). Liste `topics` sans doublons. `approved` uniquement après validation réelle selon les règles d'équipe ; un fichier sur `main` n'est pas automatiquement approuvé.
- Pour l'architecture : composants, interfaces, flux, hypothèses, erreurs/limites et compatibilité V0-V3. Pour une spécification : attentes observables, entrées/sorties, comportements d'erreur, invariants et exemples testables. Ne transforme pas une option étudiée en décision acceptée.
- Pour un runbook, impose les sections H2 non vides `## Objectif`, `## Préparation`, `## Étapes`, `## Vérifications`. `## Retour arrière` et `## Références` sont facultatives mais doivent avoir du contenu si présentes. Précise environnement, autorisations, préconditions, commandes à adapter, contrôles après chaque étape, risques, arrêts et restauration ; n'exécute pas les commandes d'exploitation sous prétexte de rédiger la procédure.
- Aucun H2 précis n'est imposé pour les DOC classiques ; organise le texte selon le sujet. Les chemins, images, MMD et ancres doivent réellement exister et être cohérents.

Les champs structurés `related_docs` acceptent **seulement des IDs DOC/RUN** publiés et existants, jamais des chemins ; `related_adrs` accepte des IDs ADR ; les chemins vont dans les liens Markdown relatifs. Ne déduis pas l'existence d'un ID d'un simple exemple de template. Une référence vers un document obsolète est possible mais déclenche un avertissement ; une cible inexistante est bloquante.

## 4. Préparer le Git et valider

1. Vérifie `git remote -v`, `git status --short --branch`, `git branch` et les PR liées avec `gh pr list`. Respecte un clone de lecture propre ; utilise un worktree distinct ou un clone d'écriture si le dossier est déjà occupé. Sur `main` propre, `git pull --ff-only` est permis ; ne le lance pas sur un worktree de modification.
2. Crée ou reprends une branche issue de `main` à jour, par exemple `docs/architecture-<sujet>`. N'écrase pas le travail d'un collègue, ne pousse jamais directement sur `main`.
3. Après rédaction, mets à jour les index/README réellement pertinents et les liens entrants touchés par un déplacement ; considère aussi les liens depuis d'autres repos si connus.
4. Lance `python scripts/validate_docs.py` (ou `python3`) depuis la racine RustkinsDocs, avec les dépendances de son `requirements.txt` installées au besoin. En présence du hook pre-commit installé, un commit exécute la même validation. Si la demande modifie **le validateur lui-même**, lance aussi ses tests `python -m pytest -q` ; une modification Markdown ordinaire n'en a pas besoin localement.
5. Optionnellement, après `git fetch origin main`, utilise `python scripts/validate_docs.py --base-ref origin/main` pour détecter des IDs perdus. Ce résultat local dépend de la fraîcheur de `origin/main` ; la PR exécute ce contrôle avec le SHA GitHub exact.
6. Inspecte `git diff --check`, le diff complet, les éventuels secrets/données privées, puis committe et pousse sur la branche dédiée. Après une erreur ou un timeout de publication, relis la branche/PR distante avant de réessayer.

## 5. PR et retour à l'utilisateur

Ouvre une PR normale dans **RustkinsDocs**, sans auto-approbation ni merge, avec `gh pr create --body-file <fichier-UTF8>`. Vérifie le corps publié via `gh pr view <numéro> --json body` et la procédure PowerShell de `rustkins-work/references/pr-workflow.md`. Précise :

- sujet, type/ID/statut des documents créés ou mis à jour, version du produit, sources de vérité ;
- changements de liens/index, sections et éventuelles implications d'ADR ;
- commandes **réellement exécutées**, résultats réels et limites/inconnues ;
- URL de la PR et checks GitHub observés via `gh pr checks` (un check non encore lancé n'est pas un succès).

La fusion et les approbations restent humaines. Le ruleset de RustkinsDocs rend `Validate documentation` obligatoire ; si une modification touche `decisions/**`, applique le parcours `rustkins-adr` pour la revue ciblée. Pour une Task/US explicite, conserve les liens Azure via `rustkins-boards` plutôt que de recopier le backlog dans le document.
