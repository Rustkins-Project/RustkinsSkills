---
name: rustkins-boards
description: Consulte et tient à jour le backlog Azure Boards Rustkins (Epic, Feature, User Story, Task, Bug, Issue), les dépendances et les preuves DoR/DoD, avec création contrôlée et reprise sûre des Tasks.
---

# Azure Boards Rustkins

Utilise ce skill pour une demande sur le backlog, une US, un sprint, une Task, un Bug, une Issue, une dépendance ou un état Azure Boards. Il peut aussi être appelé pendant un développement ou une préparation de Sprint Review. Il ne crée ni branche Git ni journal parallèle à RustkinsActivity. Lis [le workflow et les commandes](references/az-workflow.md) avant une mutation.

## Contexte obligatoire

Lis `~/.rustkins-skills/config.json` : `azure.organization` doit être une URL `https://dev.azure.com/<organisation>` et `azure.project` le projet voulu. Vérifie `az`, l'extension `azure-devops`, l'authentification et l'accès au projet avant un travail distant. Passe `--org` et, quand disponible, `--project` explicitement ; ne dépends pas du projet par défaut d'une session CLI. Ne mets aucun token dans la configuration, les arguments, le journal ou une PR. Si le CLI est absent, explique le prérequis ; n'affirme pas avoir consulté le backlog.

La source de gouvernance est le clone RustkinsDocs configuré, section `docs/project-management/`, en particulier `backlog-and-ready.md`, `definition-of-done-and-tests.md`, `agent-workflow.md`, `azure-devops-configuration.md` et `sprint-process.md`. Si ce clone manque ou est ancien, consulte la source officielle à jour avant une décision de processus.

## Lire avant d'agir

Pour une recherche, construis un WIQL borné au projet, avec les filtres demandés : type, texte, itération, état, responsable. Échappe les apostrophes WIQL. `az boards query` donne des IDs ; relis chaque work item avec `az boards work-item show --expand all -o json`. Présente l'ID et le lien, le type, le titre, l'état réel (`System.State`), l'itération, l'aire, le responsable, la description, les critères d'acceptation et les relations pertinentes. Ne conclus jamais sur le seul titre ou une sortie tronquée. Pour une US, remonte la Feature puis l'Epic, lis les Tasks enfants, Bugs/Issues associés et les liens de dépendance. Une relation manquante ou ambiguë est un écart à signaler.

Dans une vue sprint, distingue état, points d'US, Tasks et bloqueurs. Les arbitrages de sélection d'US, de sprint et de priorité appartiennent au responsable du backlog. La lecture des champs riches Azure est en HTML : conserve leur sens et cite les critères exacts utiles, sans les remplacer par un résumé affirmatif.

## Créer ou reprendre une Task

Vérifie l'US, sa Feature/Epic, ses critères d'acceptation, son itération, ses Tasks et ses dépendances. Pendant le Sprint Planning, propose les Tasks puis attends la validation du planning avant création. Pendant le développement d'une US validée, crée ou enrichis de façon autonome une Task supplémentaire qui reste dans le périmètre de l'US. Une Task décrit une action et un livrable vérifiable, avec critères de fin ; n'ouvre pas une Task distincte pour chaque modification ou pour les tests systématiques.

Utilise `scripts/boards_ops.py create-task --input <fichier-json-utf8>` avec `parent_id`, `title`, `deliverable`, `done_criteria`. Le script vérifie l'US, recherche les Tasks de même titre, crée sans responsable, lie la Task comme enfant et relit le résultat. Un appel répété réutilise seulement une Task dont parent, titre et description correspondent exactement. Toute Task candidate non liée ou différente exige une inspection humaine avant un nouvel essai. Si une création ou un lien a une issue incertaine, **relis le backlog** ; ne relance pas aveuglément la création. Vérifie ensuite les liens de dépendance utiles et ajoute-les uniquement après avoir lu les deux extrémités et leur sens. N'invente pas de dépendance.

À la prise en charge réelle, relis `Assigned To`, puis utilise `claim-task --id <id> --identity <identité-azure>`. Le script n'attribue que si le champ est vide, avec garde de révision ; il ne réaffecte jamais quelqu'un d'autre. Une Task planifiée reste non attribuée jusqu'à sa prise en charge.

## États et clôture

`set-progress --id <id> --expected <état-lu> --to <Active|Blocked|On Hold> --reason <motif>` vérifie la révision, écrit `System.State` et un historique, puis relit. `Blocked` exige un empêchement réel, son lien de dépendance et le motif ; `On Hold` une pause justifiée et sa condition de reprise. Vérifie le mappage de colonne du board après la transition. Ne déduis pas `System.State` de `System.BoardColumn`.

Pour une Task de développement terminée par PR, mets `Closed AB#<id>` dans le corps de la PR afin que l'intégration native GitHub ↔ Azure la ferme **au merge**, puis vérifie l'état. N'anticipe pas cette fermeture à l'ouverture. Une Task sans PR peut être fermée après vérification concrète du livrable et de sa DoD, avec relecture et contrôle de révision via l'API Azure. Une US peut être `Resolved` seulement si tous ses critères d'acceptation, Tasks fermées, tests et déploiement/test E2E requis sont satisfaits ; elle n'est `Closed` qu'après Sprint Review et décision humaine consignée. Applique les critères propres aux Bugs, Epics et Features ; un merge isolé ne suffit pas à déclarer un lot livré. Ne force jamais une transition refusée par les règles de l'organisation.

## Propositions et preuves

Prépare une proposition structurée avant de créer Epic, Feature ou User Story. Leur création exige une validation humaine explicite. Pour Bug ou Issue, décris le comportement observé, les preuves et la relation utile, puis applique la politique du backlog ; ne transforme pas une simple incertitude en Bug confirmé.

Évalue DoR et DoD en `satisfied`, `missing` ou `requires_human_review` pour chaque critère, avec preuve Azure/GitHub/test. N'infère pas « satisfait » d'un champ absent, d'un titre ou du succès d'une commande. Distingue la DoD de Task et celle d'US ; les critères d'acceptation, CI, tests, plateforme et revue humaine requièrent des preuves propres. Relis l'objet distant après chaque mutation et rapporte uniquement l'état confirmé.
