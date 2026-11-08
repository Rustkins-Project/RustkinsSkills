# Spécification — rustkins-boards

> **Statut :** implémenté au jalon 3 dans [`skills/rustkins-boards/`](../../skills/rustkins-boards/) ; lecture et mutations vérifiées sur le projet Azure `Test` lors de la recette intégrée. Source normative : [RustkinsDocs/project-management](https://github.com/Rustkins-Project/RustkinsDocs/tree/main/docs/project-management).

## Intention et déclencheurs

Skill utilisable seul ou appelé depuis `rustkins-work` / `rustkins-sprint-*`. Exemples : « liste mes Tasks du sprint », « décompose AB#142 », « démarre la Task #151 », « montre les dépendances de l'US » ou « prépare les éléments pour la Sprint Review ». Il ne crée pas de branche par lui-même.

**Périmètre** : Epic, Feature, User Story, Task, Bug, Issue, sprint et dépendances ; lecture, création contrôlée, mise à jour, suivi et vérification DoR/DoD. **Aucun** journal parallèle au journal Git de RustkinsActivity.

## Opérations attendues

| Capacité | Entrée et sortie attendues | Règle |
| --- | --- | --- |
| Recherche | filtres type, texte, projet, itération, état, responsable ; liste d'ID + liens | WIQL via `az boards query`, détails via `az boards work-item show` |
| Détail | ID ; tous champs utiles, AC, relations, statut, projet et provenance | Ne jamais réduire un champ riche à son seul titre |
| Hiérarchie | ID ; parent/enfants et Feature/Epic, dépendances | Relations Azure lues explicitement |
| Création Task | US parent, résultat, catégorie, critères de fin, dépendances | Rechercher duplicats puis ajouter sous le bon parent |
| Création Bug/Issue | comportement constaté, preuves et relation éventuelle | Respecter la politique du backlog |
| Création Epic/Feature/US | proposition structurée, AC, liens, estimations si déjà validées | Approbation humaine **avant mutation**, jamais création implicite |
| Attribution | Task et identité du développeur | Attribuer à la prise en charge si `Assigned To` est vide ; sinon préserver |
| Mise à jour | champs explicitement demandés, état actuel relu | Vérification avant/après, pas d'écrasement aveugle |
| DoR/DoD | work item et preuves Azure/GitHub | Retourner `satisfied / missing / requires_human_review`, pas un booléen magique |
| Sprint | itération, US, Tasks, états, SP | Les arbitrages d'US/itérations appartiennent aux humains |
| Synchronisation | références PR et travaux clôturés | Utiliser la liaison native GitHub ↔ Azure Boards ; pas de sync secondaire |

## Workflow de découpage des Tasks

1. Vérifier l'US, sa Feature/Epic, ses AC, le périmètre prévu et ses Tasks existantes.
2. Pendant le Sprint Planning : proposer et, **après validation du planning**, créer les Tasks techniques nécessaires **non attribuées**.
3. Pendant le développement : enrichir une Task existante ou créer **autonomement** une Task supplémentaire si le travail est dans le périmètre de l'US. Une Task n'est pas un log de chaque modification.
4. Chaque Task comporte un verbe d'action, un livrable vérifiable, un parent correct, ses dépendances utiles, et des critères de fin précis. Pas de Task de tests systématique distincte : les tests appartiennent au travail développé.
5. Attribuer au développeur **au moment de la prise en charge**, après avoir relu `Assigned To`. Si déjà attribuée à quelqu'un d'autre : ne pas réassigner sans demande explicite ; signaler le conflit.
6. En cas d'appel répété ou d'interruption, chercher une Task équivalente (parent + livrable + type + contexte) avant toute création.

## Gouvernance et transitions

- `New → Active` lors d'un vrai démarrage ; `Blocked` = dépendance empêchant le travail, lien/motif ; `On Hold` = pause justifiée, condition de reprise.
- Écrire **`System.State`**, jamais seulement `System.BoardColumn` ; vérifier le mappage de la colonne Azure.
- **Task de développement** : `Closed` par l'intégration native Azure Boards lors du merge de la PR qui la termine, avec `Closed AB#<id>` dans le corps. L'agent **ne clôt pas à l'ouverture de PR**.
- **Task sans PR nécessaire** : `Closed` par `az` après vérification concrète du livrable.
- **US** : `Resolved` seulement après tous les AC, toutes les Tasks fermées, tests et déploiement/test E2E satisfaits ; `Closed` uniquement après Sprint Review et décision humaine consignée.
- **Bug autonome** : `Closed AB#<id>` quand sa PR et la DoD du Bug permettent une clôture après merge. Un Bug rattaché à une US peut être traité dans sa PR.
- Les Epics/Features ne sont pas déclarés livrés par le seul merge d'une PR ; appliquer leurs critères de lot et validations.
- Un changement de sprint, de priorité ou de sélection d'US nécessite l'arbitrage du responsable de backlog, même si l'agent peut préparer le plan.

## Interface technique

Commandes métier prioritaires : `az devops configure`, `az boards query`, `az boards work-item show`, `az boards work-item create`, `az boards work-item update`, `az boards work-item relation show/add/remove`, et commandes `az boards iteration` si disponibles dans l'extension installée. **Vérifier les options et la disponibilité via `--help` au moment de l'implémentation.** Les opérations non couvertes par l'extension peuvent utiliser un appel API ciblé et documenté, sans imposer un wrapper HTTP généraliste.

- Préférer `--output json` et parser les champs par nom (notamment `System.State`, `System.AssignedTo`, `System.IterationPath` et le champ AC exact du processus).
- Ne pas mettre les descriptions HTML riches dans une chaîne shell interpolée. Préparer/valider les données en UTF-8 ; respecter le format riche effectivement attendu par Azure Boards (HTML pour les champs riches concernés).
- Distinguer `Story Points` de temps passé ; ne pas convertir arbitrairement les SP en heures.
- Un retour de CLI sans données suffisantes n'est pas une preuve de succès : relire le work item et ses relations.

## Idempotence et erreurs

- Lecture à jour **avant** mutation, recherche d'équivalent, mutation, relecture et comparaison de l'état réellement persisté.
- En cas de timeout après création : chercher l'objet candidat par parent/type/titre/contenu avant de retenter ; ne pas affirmer que `az` possède une idempotence serveur.
- En cas de conflit d'affectation, de relations incohérentes ou de modification concurrente : stopper l'écriture dangereuse et signaler le point à arbitrer.
- Refuser les transitions fictives de l'US pour améliorer les indicateurs du sprint.

## Scénarios d'acceptation

- Recherche de la Task par identifiant / filtre sprint, chargement de ses relations et AC.
- Sprint Planning crée trois Tasks distinctes non assignées ; un second appel ne les duplique pas.
- Prise en charge affecte uniquement la Task libre au profil courant ; une Task affectée à un tiers reste inchangée.
- Nouvelle Task technique découverte est liée au même parent ; nouvel Epic/US **non** créé sans accord.
- Une Task de développement reste `Active` après PR ouverte ; la clôture est demandée dans la PR et constatée **après merge**.
- Une Task de documentation sans PR est clôturée après preuve ; l'US ne devient jamais automatiquement `Closed`.
- Accents et paragraphes du titre/description préservés sur Windows et Linux.
