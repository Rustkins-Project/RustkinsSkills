---
name: rustkins-work
description: Conduit un développement Rustkins ou une reprise de PR, depuis une User Story, Task, Bug ou demande de code jusqu'à une PR GitHub prête à revoir, en coordonnant Azure Boards et RustkinsActivity.
---

# Développement Rustkins jusqu'à la PR

Utilise ce skill pour implémenter ou reprendre du code, une US, une Task, un Bug ou une review de PR dans un dépôt Rustkins. Le résultat habituel est une PR normale prête à revoir. Lis [le parcours GitHub et les mentions Azure](references/pr-workflow.md) avant de créer ou modifier une PR ; pars du [modèle de corps](assets/pr-body.md). Ce skill coordonne les autres skills sans copier leurs contrats.

## Situer et reprendre l'intervention

1. Identifie le dépôt, son remote, la branche par défaut, l'état du worktree et le développeur humain dans `~/.rustkins-skills/config.json`. Vérifie `git` et `gh` ; vérifie `az` et le projet Azure **si** un work item est concerné. Un worktree déjà modifié demande de comprendre ces modifications avant d'agir.
2. Applique [rustkins-activity](../rustkins-activity/SKILL.md) dès le début : `recover`, `discover`, reprise d'une activité cohérente ou création. Garde son `operation_id` lors d'un retry. Une PR déjà revue après une activité `completed` constitue une nouvelle intervention ; référence l'ancienne si utile.
3. Classe la demande : US existante, Task/Bug autonome, ou intervention suivie seulement par Activity. Pour un ID Azure, applique [rustkins-boards](../rustkins-boards/SKILL.md) : lis description, AC, hiérarchie, Tasks, dépendances, états et preuves DoR/DoD avant de planifier le code. Un ID absent n'est jamais déduit du titre. Propose toute nouvelle Epic, Feature ou US et attends sa validation humaine avant création.
4. Cherche dans le dépôt les branches et PR ouvertes ou fermées liées au travail, notamment celles du développeur configuré. Compare le work item, l'objectif, le dépôt et les commits. Reprends la branche/PR correspondante ; si plusieurs candidats restent crédibles, clarifie le choix. Une réponse perdue de `gh pr create`, `git push` ou de la CLI Activity impose une relecture distante avant retry.

## Réaliser

5. Si une Task Azure libre est réellement prise en charge, vérifie son responsable et utilise `rustkins-boards` pour l'attribuer au développeur et la passer à `Active` au bon moment. Préserve l'attribution d'autrui. Pour une US, réutilise ou crée les Tasks justifiées dans son périmètre ; les tests font partie des Tasks de développement.
6. Choisis une portée vérifiable et une branche explicite issue de la bonne base du dépôt. Une PR par US est le défaut ; plusieurs PR ou dépôts restent possibles si les livrables le justifient. Chaque Task de développement est rattachée à la PR qui **termine** cette Task. Travaille sur la branche du développeur concerné, sans pousser sur celle d'un collègue sans autorisation.
7. Implémente code, tests et documentation nécessaires. Exécute les tests ciblés et les contrôles applicables au dépôt. Pour une US, distingue les preuves unitaires, intégration, E2E, CI et plateforme de test exigées par RustkinsDocs ; documente les résultats réellement obtenus et ce qui reste à faire. Un test rouge ou une preuve absente empêche d'affirmer une DoD satisfaite.

## Publier et suivre

8. Committe et pousse le travail vérifié, puis crée ou mets à jour une **PR normale** dans le même dépôt. Rédige son corps dans un fichier UTF-8 avec `gh pr create --body-file` ou `gh pr edit --body-file`. Compare ensuite le corps GitHub au fichier source selon [la procédure de vérification](references/pr-workflow.md#corps-publication-et-vérification) ; vérifie base, branche, commit et état non draft. Remplis ou retire chaque emplacement du modèle.
9. Écris les mentions Azure **par work item** selon [les règles de PR](references/pr-workflow.md). Un simple `AB#` lie sans transition ; `Closed` ou `Resolved` ne s'emploient qu'après vérification des conditions de ce work item. Une PR de développement ne clôt pas une Task à l'ouverture. La fusion dans la branche par défaut est un acte humain ; relis les états Azure après la fusion au prochain point de contrôle.
10. Consulte les checks, reviews et commentaires GitHub. Corrige les remarques pertinentes sur la même PR, réponds à chaque fil traité et résous-le après vérification. Préserve les remarques qui nécessitent un arbitrage humain. En cas d'échec CI, établis la cause avant d'annoncer une PR prête.
11. Mets à jour l'Activity par sa CLI avec les commits, PR, tests et limites réels. Une Activity peut être `completed` quand le livrable attendu est une PR ouverte ; cela ne change aucun état Azure. Signale les actions post-merge et les preuves manquantes sans annoncer un work item fermé ou une US résolue avant relecture.

Review, approbation, merge de PR, acceptation d'ADR et clôture d'US en Sprint Review appartiennent aux humains. La sélection d'US, de sprint et de priorité reste sous l'arbitrage du responsable de backlog.
