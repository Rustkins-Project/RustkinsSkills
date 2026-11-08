---
name: rustkins-sprint-planning
description: Prépare un Sprint Planning Rustkins depuis Azure Boards, propose Goal, sélection et Tasks selon DoR, dépendances et disponibilités, puis applique uniquement le planning validé.
---

# Sprint Planning Rustkins

Utilise ce skill pour préparer ou appliquer un Sprint Planning. Lis le [parcours Azure](references/planning-workflow.md) avant une écriture. Les règles approuvées sont `RustkinsDocs/docs/project-management/sprint-process.md` (DOC-0028), `backlog-and-ready.md` (DOC-0025) et `agent-skills-operating-model.md`. `rustkins-boards` fournit les lectures complètes et les mutations gardées ; `rustkins-knowledge` vérifie le statut des règles. `RustkinsActivity` journalise l'intervention, sans copier le backlog.

## Préparer une proposition

1. Lis `~/.rustkins-skills/config.json`, vérifie `az`/`azure-devops`, l'organisation, le projet, l'authentification, puis trouve **l'Iteration Path de l'équipe** pour le sprint et ses dates Azure. Un nom de sprint deviné ou le seul chemin de classification du projet ne suffit pas. Lis le Product Backlog ordonné par Timothy et les US candidates avec leur Feature/Epic, AC, DoR, SP, priorité, dépendances, états et Tasks existantes. Une valeur absente reste « inconnue ».
2. Demande les disponibilités déclarées des trois personnes et les charges non développement pertinentes ; n'invente ni présence ni conversion SP → heures. Évalue les dépendances et les risques. Propose un Sprint Goal vérifiable, une sélection d'US proportionnée et quelques Tasks principales avec livrables et critères de fin. Les tests accompagnent ces Tasks.
3. Présente la proposition avec IDs/liens Azure, preuves DoR, SP connus, capacité déclarée, exclusions et effet des dépendances. **La sélection, le Goal et tout changement de périmètre attendent la validation de Timothy.** Une approbation antérieure de la même proposition reste valable ; si les faits ont changé, fais réexaminer la différence.

## Appliquer le planning validé

4. Relis chaque US et l'itération juste avant mutation. Utilise `rustkins-boards/scripts/boards_ops.py set-iteration` avec le chemin précédent exact, le sprint validé et la raison consignée. Pour chaque Task enfant inachevée déjà approuvée dans la sélection, utilise ensuite `set-task-iteration` avec son ancien chemin et l'ID de l'US ; les Tasks `Closed` conservent leur itération historique. Le script protège chaque révision et confirme le nouveau chemin. Un échec ou timeout impose une relecture de l'US et de ses Tasks avant retry.
5. Crée les nouvelles Tasks principales approuvées avec `create-task --input` du même script ; il vérifie parenté, AC, itération et doublons. Une Task existante réutilisée ne change pas d'itération automatiquement : vérifie-la et déplace-la explicitement si la sélection l'exige. Garde `Assigned To` vide jusqu'à la prise en charge réelle. Ne crée pas de Task distincte pour chaque type de test. Relis parentés, itérations, responsables et dépendances après écriture ; signale les opérations partielles sans réécrire aveuglément.
6. Rapporte le Goal et la sélection réellement validés, les IDs des Tasks créées ou réutilisées, les risques et les éléments restés au backlog. Une US non sélectionnée conserve son itération et son état.

Pendant le sprint, les changements de sélection ou de priorité reviennent à Timothy ; une Task supplémentaire dans le périmètre d'une US peut être suivie selon `rustkins-boards`.
