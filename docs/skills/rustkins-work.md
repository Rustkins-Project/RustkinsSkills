# Spécification — rustkins-work

> **Statut :** implémenté au jalon 4 dans [`skills/rustkins-work/`](../../skills/rustkins-work/SKILL.md). Ce skill orchestre le développement ; il ne remplace pas `rustkins-boards`, `rustkins-activity` ni les règles de RustkinsDocs. La recette GitHub ↔ Azure a vérifié sur le projet `Test` la liaison PR/work items, la clôture d'une Task au merge et le passage d'une US à `Resolved` au merge d'une PR distincte. La clôture `Closed` d'une US reste réservée à la Sprint Review humaine.

## Déclenchement

Demandes du type « implémente AB#142 », « continue cette US », « prends la Task 151 », « corrige les commentaires de la PR » ou intervention de code hors Azure. L'agent identifie d'abord le **niveau de suivi** (US, Task autonome, Bug autonome ou simple Activity) et le développeur humain configuré.

## Parcours standard

1. Contrôler les prérequis `git`, `gh` et les identités ; contrôler `az` et le contexte Azure si un work item est concerné. Vérifier la propreté du worktree, le dépôt et sa branche par défaut.
2. Lire l'US/Task/Bug, les AC, Tasks enfants, dépendances, DoD, documents/ADR pertinents. Chercher une activité cohérente ouverte via le skill existant `rustkins-activity` : `recover`, `discover`, reprise ou création selon son contrat.
3. Chercher les PR et branches **du développeur** et les travaux équivalents avant de créer une nouvelle branche. Ne jamais pousser dans la branche d'un autre développeur sans autorisation.
4. Si une Task libre est prise en charge, l'attribuer au développeur avec `rustkins-boards`, la passer à `Active` selon besoin et préserver l'état d'autrui.
5. Identifier la portée de la PR ; créer une branche à nom explicite, travailler sur la base du dépôt réel (pas une copie périmée), implémenter tests et documentation nécessaires.
6. Exécuter les tests ciblés puis ceux requis pour la DoD ; conserver les résultats **réels**, erreurs et limites. Ne pas inventer un succès CI ou un déploiement de test.
7. Committer, pousser, ouvrir une **PR normale (non draft)** automatiquement si vérifications satisfaites ; inclure résumé, tests, références Azure et distinction entre références et transitions. Review et merge uniquement par humains.
8. Relever les vérifications GitHub disponibles via `gh pr checks`, expliquer les échecs, corriger les retours de review **sur la même PR**. Publier les résultats et références dans RustkinsActivity ; une Activity peut être terminée alors que la Task Azure reste ouverte.
9. À la reprise, récupérer l'état réel de la PR et d'Azure : ne jamais créer silencieusement une seconde PR ou doubler une Activity.

## Granularité des PR — décision d'équipe

- **Par défaut : une PR pour une US complète**, avec ses Tasks.
- **Plusieurs PR pour la même US autorisées** lorsque le découpage le justifie, y compris dans un même dépôt ou dans plusieurs dépôts.
- **Task ou Bug sans US parente** : PR dédiée à ce work item.
- **Chaque Task de développement est rattachée à une PR qui la termine** ; si une Task s'étend sur plusieurs PR, seul son dernier changement intègre l'instruction de clôture.
- Une PR peut porter plusieurs Tasks réalisées de la même US, mais ne doit pas fermer une Task seulement citée pour contexte.
- Les modifications de review restent dans la PR existante. L'agent ne fait pas de merge, n'approuve pas sa propre PR et ne contourne pas les protections GitHub.

### Mentions Azure Boards dans le corps des PR

Pour une PR **intermédiaire** d'US `142` terminant les Tasks `151` et `152` :

```text
AB#142
Closed AB#151
Closed AB#152
```

Pour la PR **finale** terminant la Task `153`, et **seulement si** les preuves AC/tests/déploiement E2E existent **avant merge** et que les dernières Tasks seront clôturées par ce merge :

```text
Resolved AB#142
Closed AB#153
```

Pour une Task/Bug autonome : `Closed AB#<id>` si la PR complète le travail et que les conditions sont réunies.

**Attention :** l'application Azure Boards interprète un état ou catégorie placé avant `AB#id` à la fusion dans la **branche par défaut** ; une simple mention `AB#id` crée un lien sans transition. Les transitions invalides peuvent être ignorées. Utiliser un mot-clé de transition **par work item**, ne pas supposer qu'un seul `Closed` s'applique à une liste d'IDs. Éviter tout `Fixes AB#...` involontaire dans commits et PR.

Référence : https://learn.microsoft.com/en-us/azure/devops/boards/github/link-to-from-github?view=azure-devops

### Conditions de la PR finale

La « dernière PR créée » n'est **pas** nécessairement la « dernière mergée » : les précédentes doivent être intégrées avant le merge final. Les agents préparent des liens/une dépendance de review explicites et vérifient les autres PR en cours. Si la situation évolue avant merge, modifier la description de la PR finale et retirer le mot-clé `Resolved` tant que la DoD n'est plus certaine.

La **DoD officielle de l'US** comporte les AC, toutes les Tasks `Closed`, tests unitaires, intégration et E2E, déploiement sur la plateforme de test et preuves de la révision réellement testée. **Ne pas changer la DoD par commodité.** Les dernières Tasks peuvent devenir `Closed` pendant le même merge que la demande `Resolved`. Vérifier **après merge** que toutes les Tasks sont réellement `Closed` et l'US `Resolved`, sans présumer d'un ordre des transitions. Si Azure refuse les transitions simultanées, ou si le déploiement/test E2E n'est possible qu'après merge, utiliser `AB#142` sans `Resolved`, puis résoudre l'US via `rustkins-boards` après constat de la DoD complète. L'US n'est `Closed` qu'à la Sprint Review.

Une PR finale pouvant clôturer ses dernières Tasks lors du même événement que la demande de `Resolved`, ne pas supposer que l'application effectue ces transitions dans un ordre garanti. Prévoir une **vérification post-merge au prochain point de contrôle** pour constater les états et traiter un éventuel échec.

## Branches, commits et traçabilité

- Nom de branche recommandé : `feature/<us-id>-<slug>`, `task/<id>-<slug>`, `fix/<bug-id>-<slug>` ; ajouter un suffixe pour plusieurs PR sans collisions.
- Pour chaque repo : une branche/PR **dans ce repo** ; une PR ne peut pas traverser plusieurs dépôts.
- Travailler sur une branche de travail dédiée ; jamais pousser `main` pour le code.
- Utiliser `gh pr create --body-file <fichier-utf8>` puis `gh pr edit <numéro> --body-file <fichier-utf8>` pour toute description multiligne, y compris les corrections de review. Suivre la [procédure PowerShell et sa vérification du corps publié](../installation-and-quality.md#corps-de-pr-multiligne-dans-powershell). Ne pas compter sur le titre seul pour la liaison Azure.
- Les mentions `AB#...` dans les commits sont à considérer avec prudence : aucun verbe de fermeture involontaire.
- La PR doit décrire la cible, les Tasks terminées, le plan de tests, les risques, les preuves et les dépendances de merge.

## Frontières de sécurité

- Ne jamais publier des secrets, tokens, réponses Discord privées, historiques complets de conversation ou données personnelles sans besoin.
- Nouvelle US/Epic/Feature hors backlog : s'arrêter à une proposition et demander accord humain avant écriture.
- Conflit de DoD, de périmètre, d'ADR ou de prise en charge par un autre humain : faire arbitrer.
- Branch protection, review et merge humains restent les garde-fous de qualité ; pas de prise de pouvoir sur le dépôt par l'agent.

## Critères de recette

1. Une Task non assignée est prise en charge sans modifier celles des collègues.
2. Une US mono-PR reçoit `Closed AB#task` et, si DoD vérifiée, `Resolved AB#us`.
3. Deux PR de la même US : la première lie l'US sans transition, la seconde ne demande `Resolved` qu'après intégration des premières et DoD complète.
4. Même US sur deux repos : deux PR liées à l'US, aucune clôture prématurée.
5. Retour de review : l'agent corrige dans la même PR, pas de nouvelle branche/PR.
6. Échec de tests ou environnement de test absent : aucune fausse réussite ni `Resolved` anticipé.
7. Test GitHub ↔ Azure sur work items de test : vérifier **l'état réel après merge**, jamais déduire la réussite de la syntaxe seule.
