# Spécifications — les trois skills de sprint

> **Statut :** à implémenter **après le premier lot de cinq skills**. Ces skills s'appuient sur `rustkins-boards` et `rustkins-knowledge`. Les règles de référence figurent dans [RustkinsDocs/sprint-process](https://github.com/Rustkins-Project/RustkinsDocs/blob/main/docs/project-management/sprint-process.md).

## Gouvernance commune

Les Epics sont des **versions produit**, jamais des sprints. Les Epics, Features et US sont préparés principalement **avant le développement** ; les agents peuvent proposer un nouvel élément de périmètre, mais la création d'une US/Feature/Epic non prévue exige accord humain. Les sprints représentent des itérations Azure, identifiées par leurs véritables `Iteration Path`.

Trois développeurs sur leur temps libre ; pas de Daily obligatoire. Les disponibilités sont déclarées par les humains. Story Points **relatifs** pour les US ; pas de conversion automatique en heures. Les tests accompagnent les Tasks de réalisation.

## rustkins-sprint-planning

**Entrées** : sprint / dates déjà établies dans Azure, Product Backlog ordonné, priorités, dépendances, DoR, capacités/disponibilités réelles, US candidates, retours du sprint précédent.

**Proposer avant d'écrire** :
1. Lire le sprint réel et les US candidates dans Azure Boards ; distinguer priorité et dépendance.
2. Vérifier INVEST/DoR, AC, estimations SP et risques ; afficher clairement les informations manquantes.
3. Proposer un Sprint Goal vérifiable et une sélection d'US réaliste pour les trois personnes.
4. Demander validation humaine de la sélection, du Goal et des changements de périmètre ; ne pas modifier `Iteration Path` en anticipant le consentement.
5. Après validation : affecter les US au sprint, créer les Tasks principales **sans `Assigned To`** ; descriptions et critères de fin, parenté et dépendances exacts.
6. Autoriser ensuite `rustkins-work` à adapter les Tasks de manière autonome pendant le développement, sans changer les US du sprint.
7. Produire une synthèse du planning avec liens Azure et décisions réellement approuvées.

**Recette** : pas de duplication au second passage ; Tasks non attribuées ; US non sélectionnées intactes ; effort non-dev pris en compte ; priorité/estimation non inventée.

## rustkins-sprint-status

**Entrées** : sprint courant, date de constat, liens Azure et GitHub ; synthèse éventuellement enrichie par RustkinsActivity.

1. Lire les US et Tasks du sprint, leurs états `System.State`, dépendances et responsables actuels.
2. Consolider PR ouvertes/mergées et CI via `gh` ; distinguer un signal `green` d'une vraie preuve de déploiement/test E2E.
3. Rapporter nombre d'US par état, Tasks actives/bloquées, SP engagés, SP **réellement livrés** (US `Closed` après Review), risques de report et dépendances.
4. Rendre visibles `Blocked` vs `On Hold` et ne pas compter une US `Resolved` comme livrée.
5. Proposer les actions utiles sans changer silencieusement le Sprint Goal ni les engagements.
6. Fournir un rapport textuel concis ou détaillé à la demande, avec données vérifiables ; pas d'agent permanent ni cron obligatoire.

**Recette** : les états proviennent de `System.State`, pas des seules colonnes ; SP livrés ne comprennent pas les US `Resolved` ; liens CI vérifiables ; métriques inconnues explicites.

## rustkins-sprint-close

**Entrées** : sprint, US `Resolved`, AC, tests, environnement de test, PR, décideurs humains, décisions de review, constats de rétrospective.

1. Préparer la Sprint Review depuis les preuves réelles, signaler les US non éligibles ; générer une trame de validation.
2. Pendant/après la review, **recueillir la décision humaine pour chaque US** ; seulement alors passer `Resolved → Closed` via `rustkins-boards`, en consign ant la décision dans le compte rendu.
3. Si un AC/DoD initial échoue : remettre à `Active` sur décision traçable ; si l'US est conforme mais qu'une amélioration nouvelle est demandée, proposer un nouveau work item.
4. Rédiger `review.md` et `retrospective.md` sous `docs/project-management/sprints/<sprint>/` dans RustkinsDocs ; participants, date, objectifs, décisions, preuves, constats et actions.
5. Identifier les US inachevées, leurs Tasks ouvertes et états `Blocked`/`On Hold` ; préparer le report pour validation du responsable backlog. Déplacer uniquement après validation, sans refermer/réouvrir artificiellement des Tasks terminées.
6. Recenser les actions d'amélioration utiles, attribuées humainement et proportionnées à une équipe de trois.

**Recette** : aucune US `Closed` sans décision de review, comptes rendus présents, report conserve états légitimes, SP des US inachevées non crédités, nouvelle évolution différenciée d'un AC échoué.

## Dépendances techniques

Aucune API serveur nouvelle nécessaire. Utiliser les requêtes et mutations `az` de `rustkins-boards`, `gh` pour la CI/PR, et Git/PR de `rustkins-knowledge` pour publier les comptes rendus. L'initialisation d'une itération Azure doit être vérifiée sur la version exacte de `az` ; si une opération de gestion d'iteration est absente de la CLI, documenter un appel API ciblé ou une action humaine plutôt que prétendre qu'une commande inexistante fonctionne.
