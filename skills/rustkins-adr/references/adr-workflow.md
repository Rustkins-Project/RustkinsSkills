# Parcours de création, évolution et remplacement d'une ADR

Références **à relire dans la révision réelle de RustkinsDocs** : `decisions/README.md`, `docs/conventions/knowledge-management.md`, `templates/adr.md`, `schemas/adr.schema.json`, `docs/specifications/documentation-validation-ci.md` et les ADR applicables. Le présent guide décrit le travail de l'agent ; le dépôt source prévaut si ses règles évoluent.

## 1. ADR ou document ordinaire ?

Une ADR consigne **pourquoi** une équipe retient ou envisage une option et les compromis correspondants. La description d'un composant, un contrat YAML/API, un tutoriel ou un relevé de réunion n'est **pas** automatiquement une décision. Les comportements décidés peuvent ensuite être reflétés dans les spécifications ou l'architecture via `rustkins-docs`, avec les références croisées appropriées.

Avant création, recherche la même décision, les sujets proches, les versions concernées, les ADR rejetées/remplacées, et les spécifications en vigueur. Les titres ou IDs trouvés dans un document historique ne prouvent ni la présence d'une ADR dans `decisions/` ni son statut accepté. Une réponse validée de `rustkins-ask-team` est une **source documentable**, jamais une approbation GitHub.

Si la décision est encore indéterminée, produis des alternatives et questions factuelles. N'attribue pas d'avis aux membres de l'équipe sans référence et ne les contacte pas sans autorisation.

## 2. Préparer l'identifiant et le frontmatter

- Vérifie `main`, la branche de travail et les PR ouvertes ; cherche les IDs `ADR-xxxx` utilisés ou en cours d'ajout. `ADR-0000` est réservé à `templates/adr.md`. Le prochain numéro apparent peut entrer en conflit avec une PR concurrente : recontrôle avant push, puis laisse le contrôle sur le commit de fusion détecter une collision éventuelle.
- Travaille dans une branche ou un worktree **d'écriture** propre, sans écraser une autre intervention. Ne supprime, ne recycle et ne renomme l'ID d'aucune ADR déjà publiée, même `rejected` ou `superseded`.
- Copie le **template du dépôt courant** et remplis les champs exigés par `schemas/adr.schema.json`. Une nouvelle proposition présente ce frontmatter de principe :

```yaml
---
id: ADR-1234  # Exemple uniquement : vérifier qu'il est libre
title: "Titre explicite de l'arbitrage"
status: proposed
topics: [architecture]
applies_to: [V1]
decided_at: null
approved_by: []
supersedes: []
related_work_items: []
references: []
---
```

Les champs `references` attendent des URI absolues valides ; utiliser `[]` si aucune référence externe réelle n'existe. `related_work_items` contient des IDs numériques Azure seulement s'ils sont connus. Ne crée pas de `related_docs` sur une ADR si le schéma actuel ne l'autorise pas. `applies_to` n'admet que `V0`, `V1`, `V2`, `V3`, ou `all` seul.

## 3. Corps Markdown obligatoire et qualité de l'analyse

La PR doit contenir quatre sections H2 **non vides** :

- `## Contexte` : problème, objectif, portée, état existant, contraintes (résilience, exploitation, sécurité, compatibilité, coûts) et sources.
- `## Décision` : option **envisagée** pour une `proposed` ; choix, architecture proposée, limites et conditions. Ne pas rédiger une proposition comme un fait déjà accepté.
- `## Alternatives` : options crédibles réellement examinées, avantages/inconvénients, critères comparatifs ; ne pas inventer de POC ou de benchmarks.
- `## Conséquences` : bénéfices, trade-offs, risques, migration, observabilité, dette, coût opérationnel et impact sur les versions.

Des H2 supplémentaires sont possibles, dont `## Références`. Toutes les sections obligatoires doivent contenir de la matière ; une ligne de commentaire HTML ou un titre isolé ne compte pas comme contenu. Une alternative non évaluée reste signalée comme telle. Ne déclare jamais un test, un coût mesuré, une décision ou une date sans source.

Un exemple de structure valide (sans présumer du contenu d'une décision) :

```markdown
# Titre de l'ADR

## Contexte

Décrire le problème concret et les contraintes établies.

## Décision

Proposer l'option A, en attendant la validation humaine.

## Alternatives

Comparer A et B avec les critères connus et les inconnues.

## Conséquences

Décrire les changements, les compromis et les vérifications futures.
```

## 4. Statuts et remplacement sans fausse approbation

| Situation | Action de l'agent | Garde |
| --- | --- | --- |
| Nouvelle ADR | Préparer `proposed`, `decided_at: null`, `approved_by: []` et une PR | Review humaine requise avant merge ; même mergée, la proposition n'est pas une ADR acceptée |
| Équipe n'a pas encore statué | Conserver `proposed`, expliquer le point ouvert | Ne pas se déclarer approbateur |
| Équipe a décidé d'accepter | Préparer les changements `accepted` **seulement avec une décision réelle et vérifiable**, et approbateur/date authentiques | Revue par un **autre humain** et merge sur `main` ; l'agent ne publie pas seul l'acceptation |
| Proposition refusée | Préserver le fichier et consigner `rejected` si réellement tranché | Pas d'effacement d'historique |
| Ancienne ADR remplacée | Nouvelle ADR avec `supersedes` pointant vers des IDs existants | Si nouvelle `proposed`, laisser les anciennes acceptées en l'état |
| Remplacement finalement accepté | Dans **une même PR**, nouvelle `accepted` et **toutes** les anciennes ciblées `superseded` | Préserver les fichiers, au moins une ADR acceptée remplace chaque ADR supersédée |
| Cycle, auto-référence ou cible absente | Corriger la modélisation, ne pas publier | Le validateur doit bloquer |

Le graphe accepte une ancienne ADR remplacée par plusieurs nouvelles ADR acceptées ; il interdit auto-remplacement et cycles. Ne modifie jamais le statut de l'ancienne ADR trop tôt : le validateur exige qu'une ADR `superseded` soit remplacée par au moins une `accepted`. Lors de la promotion d'une proposition déjà mergée, une **nouvelle PR** avec la transition et les éventuels changements sur les anciennes ADR est nécessaire.

GitHub impose à `decisions/**` une approbation de `rustkins-team` distincte de l'auteur, en plus du check obligatoire `Validate documentation`. Le champ YAML `approved_by` et une réponse Discord ne remplacent **jamais** cette review.

## 5. Validation, publication et compte rendu

1. Vérifie `git status --short --branch`, la base `main` et les PR ouvertes ; reprends une branche/PR du même sujet si elle existe. Un clone de lecture sale n'est pas à resynchroniser aveuglément.
2. Rédige depuis les templates et sources cités, liens Markdown relatifs existants, et mets à jour `decisions/README.md` ou les index pertinents lorsque cela aide à trouver l'ADR ; évite les doublons.
3. Depuis la racine RustkinsDocs, exécute `python scripts/validate_docs.py` (ou `python3`) ; corrige les erreurs de sections, frontmatter, références ou statuts. Le pre-commit local exécute la même validation si installé. Facultatif avec une base à jour : `git fetch origin main` puis `python scripts/validate_docs.py --base-ref origin/main`.
4. Relis `git diff --check` et le diff complet ; exclue secrets, transcriptions ou liens privés sensibles. Committe et pousse sur une branche, puis crée une PR normale via `gh pr create --body-file <fichier-UTF8>`. Vérifie les sauts de ligne du corps GitHub comme dans `rustkins-work/references/pr-workflow.md`.
5. La PR explique : question à trancher, options, recommandation si fondée, statut `proposed` ou transition humaine établie, `applies_to`, IDs `supersedes`, sources, tests exécutés et risques. Consulte `gh pr checks`/reviews ; un check en attente n'est pas vert. **Ne clique pas sur Merge**, n'auto-approuve pas, n'essaie pas de contourner le ruleset.
6. À la reprise, relis la PR et les décisions humaines réelles. Si l'équipe accepte la proposition, prépare la transition autorisée et cohérente ; ne change pas le YAML avant de disposer d'une preuve de la décision. La fusion effectuée par une personne ne permet pas d'inférer rétroactivement l'acceptation d'une proposition restée `proposed`.

Le travail documentaire utilise `git` et `gh`; si une Task/US doit être suivie, sollicite `rustkins-boards`. Pour toute contradiction factuelle entre ADR acceptées ou avec une spécification officielle, expose-la et fais arbitrer au lieu d'en choisir une silencieusement.
