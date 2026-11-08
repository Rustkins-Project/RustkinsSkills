# Architecture cible de RustkinsSkills

> **Statut :** architecture cible ; les jalons 1 à 6 et les skills de sprint du jalon 8 sont implémentés. La recette intégrée du jalon 7 a vérifié les liens et transitions GitHub/Azure ainsi que la réponse Discord validée ; les cas de sprint demandent encore une recette sur une itération réelle.
> **Périmètre :** outillage des trois développeurs avec Codex et Claude Code ; ce projet n'est pas le moteur CI/CD Rustkins.

## Principes validés

1. **Cinq skills dans le premier lot** : `rustkins-activity` (existant), `rustkins-boards`, `rustkins-work`, `rustkins-ask-team`, `rustkins-knowledge`.
2. **Skills de sprint dédiés ensuite** : `rustkins-sprint-planning`, `rustkins-sprint-status`, `rustkins-sprint-close`. Leur contrat est conçu dès maintenant.
3. `gh` + `git` pour GitHub et les dépôts locaux, `az` + extension `azure-devops` pour Azure Boards. Les appels HTTP directs restent permis **en cas de besoin avéré** ; Discord Bot utilise nécessairement son API privée. Ne pas reconstruire un serveur intermédiaire.
4. `RustkinsMCP` est **historique seulement**, jamais une dépendance d'installation ou d'exécution ; ne pas réutiliser son journal SQLite.
5. Les agents réalisent le développement jusqu'à la PR prête à revoir, **sans demander une validation supplémentaire** pour brancher, coder, tester, committer, pousser et ouvrir la PR. Review et merge humains, jamais par l'agent.
6. **Pas de versionnement par skill** (ni manifest semver, ni négociation de compatibilité) : installation des fichiers du clone local de RustkinsSkills et mise à jour par `git pull` puis `install.py`.
7. Le français et les caractères Unicode sont de première classe sous Windows/PowerShell et Linux. Les sources, fichiers temporaires, entrées et sorties sont UTF-8.

## Responsabilités et source de vérité

| Domaine | Source de vérité | Responsable dans Skills | Accès |
| --- | --- | --- | --- |
| Backlog, sprints, états, dépendances, DoR/DoD | Azure Boards | `rustkins-boards` | `az boards` ; API seulement si CLI insuffisante |
| Code, branches, PR, reviews, CI | GitHub / clone de travail | `rustkins-work` | `git`, `gh` |
| Interventions, brouillons, reprise, journal Git | RustkinsActivity | `rustkins-activity` **existant** | CLI Rust existante |
| Décisions, spécifications, ADR et notes | RustkinsDocs | `rustkins-knowledge` | clone Git, `gh` |
| Questions avec réponse humaine validée | RustkinsDiscordBot | `rustkins-ask-team` | API `/internal/questions` |
| Planification et rituels du sprint | Azure Boards + RustkinsDocs | skills `rustkins-sprint-*` | `rustkins-boards`, `rustkins-knowledge` |

Un skill décrit **les décisions de l'agent** et délègue les opérations déterministes aux commandes natives ou à des scripts testés. Il ne joue ni le rôle d'une API distante, ni celui d'un service permanent. Aucune synchronisation autonome entre deux sessions d'agent n'est supposée.

### Composition

- `rustkins-work` coordonne, selon le besoin, `boards`, `activity`, `knowledge` et `ask-team` ; il ne copie pas leurs contrats.
- Chacun des quatre autres skills est également utilisable directement : par exemple « liste les Tasks du sprint » n'ouvre pas de branche.
- Les scripts locaux sont réservés à l'encodage des payloads complexes, à la validation, à la réconciliation, aux prérequis et aux opérations répétitives sujettes aux erreurs ; **pas de wrapper systématique pour chaque commande CLI**.
- Une décision issue de Discord n'est pas automatiquement une ADR acceptée. Une Activity terminée ne signifie ni Task Azure `Closed`, ni US `Resolved`.

## Autonomie et gouvernance

| Action | Autorisation |
| --- | --- |
| Lire les sources / rechercher les doublons | Autonome |
| Créer/adapter une Task justifiée dans une US existante | Autonome ; parent, livrable, dépendances, non-duplication |
| Attribuer une Task non assignée au développeur prenant le travail | Autonome ; ne jamais réattribuer silencieusement |
| Créer un Bug distinct justifié | Autonome selon la politique RustkinsDocs ; engagement dans le sprint soumis à arbitrage |
| Créer un Epic, une Feature, une US hors backlog préparé | Proposition puis accord humain avant écriture |
| Ajouter/retirer/replanifier une US en sprint | Arbitrage du responsable de backlog (voir RustkinsDocs) |
| Brancher, committer, pousser et ouvrir une PR de développement | Autonome avec tests et vérifications, sans merge |
| Accepter une ADR / fusionner une PR / clore une US à la Sprint Review | Humain uniquement (agent peut préparer et exécuter une mise à jour explicitement autorisée) |

En cas d'erreur, ne jamais afficher de succès non vérifié. Rechercher l'état réel avant nouvelle tentative, surtout après timeout : la commande a peut-être abouti.

## Contrats et documentation

- [Plan d'implémentation](implementation-plan.md)
- [Configuration, UTF-8 et recette](installation-and-quality.md)
- [Boards](skills/rustkins-boards.md) · [Work](skills/rustkins-work.md) · [Ask team](skills/rustkins-ask-team.md) · [Knowledge](skills/rustkins-knowledge.md)
- [Skills de sprint](skills/sprints.md)
- [RustkinsDocs : gouvernance](https://github.com/Rustkins-Project/RustkinsDocs/tree/main/docs/project-management)
- [RustkinsDiscordBot : contrat D2](https://github.com/Rustkins-Project/RustkinsDiscordBot/blob/main/docs/01-cahier-des-charges.md)
- [RustkinsActivity : contrat de la CLI](https://github.com/Rustkins-Project/RustkinsActivity/blob/main/docs/agent-cli.md)

Les règles métier validées dans RustkinsDocs prévalent sur les exemples locaux. En cas de contradiction, signaler le conflit plutôt que le résoudre implicitement.
