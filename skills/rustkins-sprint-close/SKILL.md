---
name: rustkins-sprint-close
description: Prépare Sprint Review, rétrospective et report Rustkins ; applique les décisions humaines de clôture des US avec garde de révision et publie les comptes rendus dans RustkinsDocs.
---

# Clôture de sprint Rustkins

Utilise ce skill pour préparer ou reprendre la fin d'un sprint. Lis le [parcours de review et de report](references/close-workflow.md). Les règles approuvées sont `RustkinsDocs/docs/project-management/sprint-process.md` (DOC-0028), `definition-of-done-and-tests.md` (DOC-0027) et `agent-skills-operating-model.md`. `rustkins-boards` garde les mutations ; `rustkins-knowledge` publie les comptes rendus, `rustkins-work` fournit les preuves PR/CI et `RustkinsActivity` journalise l'intervention.

## Préparer, puis recueillir les décisions

1. Identifie le sprint réel et relis toutes ses US/Tasks, leurs AC, états, responsables, dépendances, PR, tests, déploiement et E2E. Prépare pour chaque US `Resolved` une démonstration et une évaluation DoD avec liens. Une US non `Resolved` ne se présente pas comme livrée ; distingue un AC initial échoué d'une amélioration nouvelle.
2. Prépare la trame de `review.md` et `retrospective.md` dans `RustkinsDocs/docs/project-management/sprints/<sprint>/` selon les conventions documentaires du dépôt. Garde les décisions encore inconnues explicitement en attente. Ces deux comptes rendus sont nécessaires pour chaque sprint, même si aucune US n'est acceptée.
3. Pendant/après la review, recueille la décision humaine explicite pour chaque US et ses participants. Une acceptation d'US conforme permet `Resolved → Closed` ; un AC initial manqué demande `Resolved → Active` avec motif et report. Une amélioration hors AC devient une proposition distincte. Une réponse Discord ne remplace pas la décision de Sprint Review. Complète alors les comptes rendus avec Goal, démonstrations, décisions **par US**, preuves, remarques, reports, constats de rétrospective et actions attribuées. Publie une PR documentaire normale via `rustkins-knowledge` et vérifie son corps.

## Appliquer et relire

4. Après documentation de la décision, prépare le JSON de `rustkins-boards/scripts/boards_ops.py review-story --input`. Le script exige une US `Resolved`, le sprint exact, un lien de compte rendu, des participants et un motif ; il refuse de fermer une US ayant une Task enfant ouverte. Il applique l'état sous garde de révision et relit le résultat. La vérification humaine des AC, de la DoD et du compte rendu reste indispensable avant l'appel.
5. Pour les US inachevées, conserve `New`, `Active`, `Blocked` ou `On Hold` selon la réalité ; prépare le report de chaque US **et de ses Tasks inachevées** avec son effet sur le Sprint Goal pour Timothy. Après son arbitrage, utilise `set-iteration` sur l'US puis `set-task-iteration` sur chaque Task inachevée approuvée, avec ancien chemin exact et motif ; relis tous les résultats. Les Tasks `Closed` restent fermées dans leur itération historique ; ne crédite aucun SP partiel. Les SP livrés viennent seulement des US `Closed` en review.
6. Relis les décisions et états Azure, les comptes rendus et leurs liens ; consigne tout écart ou opération incertaine pour reprise. Une PR documentaire ouverte ne vaut pas une PR mergée, et aucune clôture n'est déduite d'une commande sans relecture.

La review, l'approbation de la PR documentaire, la fusion et l'arbitrage du report appartiennent aux humains ; l'agent peut préparer et exécuter une mutation Azure explicitement autorisée par leur décision.
