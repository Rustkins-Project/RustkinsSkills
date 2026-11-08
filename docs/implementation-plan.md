# Bilan d'implémentation de RustkinsSkills

> **Statut au 9 novembre 2026 :** les jalons 1 à 8 sont livrés sur `main` : installateur, helpers, huit skills et recette intégrée sur données de test. La recette des trois skills de sprint sur une itération réelle, avec Sprint Review et rétrospective, reste à conduire. Ce document conserve les critères de conception et les scénarios pour les vérifications futures.

## Hypothèses et prérequis

- Équipe de trois personnes, postes Windows et/ou Linux, Codex ou Claude Code.
- `RustkinsActivity` et son skill actuel restent opérationnels ; aucune réécriture.
- Projet Azure DevOps configuré avec Azure Boards et processus d'états décrit dans RustkinsDocs.
- Azure Boards for GitHub installé sur les repos nécessaires ; `AB#<id>` relie, `Closed AB#<id>` et `Resolved AB#<id>` demandent une transition au merge **sur la branche par défaut**.
- `RustkinsDiscordBot` expose déjà POST/GET `/internal/questions`. Pas de nouvelle API à coder pour le premier lot.
- Aucun composant de `RustkinsMCP` n'est requis.

## Jalons livrés et limites de recette

| Étape | Livraison sur `main` | Recette et limite |
| --- | --- | --- |
| **0 — Alignement documentaire** | Cadrage Skills, Docs et DiscordBot | Les règles de DoD et de transitions ont été alignées. |
| **1 — Installateur commun** | Installation dynamique de tous les dossiers `skills/*` pour Codex et Claude Code | `install.py --check` reconnaît les huit skills ; installation sur ce poste vérifiée. |
| **2 — Socle CLI/UTF-8** | Helpers `az`/`gh`, JSON, HTML et Markdown UTF-8 | Tests Windows et Linux réussis ; lancement Azure CLI Windows et corps de PR multiligne corrigés. |
| **3 — rustkins-boards** | Skill, guide Azure et scripts de mutation | Lecture, création de Task et transitions vérifiées sur le projet Azure `Test`. |
| **4 — rustkins-work** | Skill, guide de PR et modèle de corps | Liaison de PR et transitions natives après merge vérifiées avec `test#2` et `test#3`. |
| **5 — rustkins-ask-team** | Skill et client HTTP local reprenable | Question réelle publiée sur le bot local ; réponse humaine validée relue. |
| **6 — rustkins-knowledge** | Skill de recherche et contribution documentaire | Recherche de source approuvée vérifiée ; aucune ADR réelle proposée ou approuvée pendant la recette. |
| **7 — Premier parcours intégré** | Ajustements d'intégration et recette des cinq premiers skills | Parcours sur données de test vérifié ; US `Resolved` contrôlée après merge, sans clôture `Closed` hors review. |
| **8 — Skills de sprint** | `rustkins-sprint-planning`, `rustkins-sprint-status`, `rustkins-sprint-close` | Tests automatisés Windows/Linux réussis ; aucune recette complète sur une itération réelle. |

Les cinq skills du premier lot et les trois skills de sprint sont disponibles. Le tableau distingue le code livré des parcours effectivement exercés.

## Critères de livraison par étape

### Étapes 1 et 2 — installateur / helpers

- `install.py` parcourt `skills/` sans liste de noms codée en dur et installe une copie identique pour chaque agent ; installation atomique ou reprise propre si interruption.
- Chaque skill expose son `SKILL.md` et ses `references/`/`scripts/` lorsqu'ils existent.
- L'absence d'un prérequis propre à un skill donne un message exploitable et n'empêche pas l'usage des autres quand c'est possible.
- Configuration locale **sans secret** : profil humain, login, chemins des clones, organisation/projet Azure, base URL Discord ; authentification par les outils et coffre local/environnement.
- Une réinstallation sans arguments conserve les réglages ; pas de versionnement de skill, pas de migration semver.

### Étape 3 — Azure Boards

- Lire les Epics, Features, US, Tasks, Bugs, Issues ; champs métier, états, itération, responsable, AC et relations.
- Vérifier les doublons avant création, créer les Tasks d'une US après Sprint Planning et pendant le développement si nécessaire ; pas de Task de test dédiée automatiquement.
- `Assigned To` vide au Sprint Planning ; affectation du développeur à la **prise en charge** d'une Task non attribuée.
- Une US/Epic/Feature manquante est **proposée**, jamais créée sans accord ; ajout/retrait d'US d'un sprint arbitré par l'humain compétent.
- États et DoD conformes à RustkinsDocs ; pas de `Closed` automatique d'US.

### Étape 4 — développement et PR

- Recherche d'Activity en cours, d'US/Tasks, branches et PR avant création.
- Une PR par US **par défaut** ; plusieurs PR et plusieurs repos autorisés si nécessaire ; chaque Task est clôturable par **la PR qui finit cette Task**.
- PR intermédiaires : `AB#<us>` + `Closed AB#<task>` pour chaque Task réellement achevée.
- PR finale : `Resolved AB#<us>` **uniquement** lorsque les autres PR sont déjà mergées, les AC/tests/validation de test sont prouvés et les dernières Tasks seront clôturées au même merge ; vérifier ensuite que toutes les Tasks sont réellement `Closed` et l'US `Resolved`. Si les états ne peuvent pas évoluer simultanément ou si la validation est post-merge, utiliser `AB#<us>` puis passer l'US à `Resolved` après vérification.
- Pour Bug/Task autonome, `Closed AB#<id>` sur la PR terminant le travail.
- Aucun `Resolved` anticipé : si la plateforme de test n'est disponible qu'après merge, l'agent finalise alors l'US via `az` après vérification effective.
- CI et review humaine avant merge ; GitHub/Azure natif pour liens et transitions, **pas de GitHub Action de clôture personnalisée** dans ce lot.

### Étapes 5 et 6 — décisions et connaissance

- Question Discord par API privée, clé d'idempotence durable, rappel du `question_id` au développeur ; aucune attente infinie en session, aucune auto-réponse.
- ADR en PR revuable par un autre humain ; note `knowledge/` avec statut honnête et preuve ; lecture prioritaire des sources canoniques.

## Scénarios de recette transverses

1. **Français** : `Échec d'exécution — coût déjà payé`, apostrophe, accents, emoji et texte multiligne survivent à `az`, `gh`, Python, aux PR et aux fichiers UTF-8, Windows et Linux.
2. **Tâches** : une US déjà créée reçoit des Tasks au planning non assignées ; un développeur en prend une ; une nouvelle Task technique utile est créée sans doublon.
3. **PR simple** : une PR termine l'US, closes les Tasks dans sa description et demande `Resolved` uniquement si DoD pré-merge complète ; aucun merge agent.
4. **PR multiples** : deux PR intermédiaires lient l'US et ferment leurs Tasks ; la PR de fin, mergée en dernier, seule demande `Resolved`. Contrôler les transitions réelles sur work items de test.
5. **Déploiement après merge** : PR finale ne contient pas `Resolved` ; après déploiement + E2E, transition `az` `Active → Resolved`, jamais `Closed`.
6. **Erreurs/retry** : commande échouée ou accusé perdu ; relire le remote avant retry, aucune PR/Task/question en double.
7. **Discord** : POST idempotent, GET pending, puis answered après validation humaine ; aucune réponse supposée.
8. **Sprint** : pas de réaffectation silencieuse, pas d'US ajoutée au sprint sans arbitrage, report correct, bilan ne compte comme livrés que les SP des US `Closed` en Sprint Review.

## Vérifications encore nécessaires

- Exercer `rustkins-sprint-planning`, `rustkins-sprint-status` et `rustkins-sprint-close` sur une itération Azure réelle, avec sélection humaine, dates, disponibilités, Sprint Review et rétrospective.
- Tester une contribution ADR réelle seulement lorsqu'une décision documentaire le justifie ; son approbation et sa fusion restent humaines.
- Conserver les scénarios transverses ci-dessus pour les régressions et vérifier les états Azure réellement persistés après chaque merge.

## Risques à contrôler

- Conflit entre `Resolved` au merge et les E2E sur plateforme de test : **ne pas atténuer la DoD** pour simplifier les PR.
- Une PR finale créée tôt mais mergée avant une PR intermédiaire : retirera le droit à `Resolved` ; vérifier à nouveau avant le merge.
- L'application Azure Boards peut ignorer une transition invalide ; contrôler `System.State` après merge plutôt que présumer le succès.
- Les APIs/CLI évoluent ; adapter une commande après une petite preuve locale, sans introduire une dépendance au MCP.
- Plusieurs agents ou retries peuvent créer des doublons ; réconciliation par état réel, aucune clé d'idempotence fictive pour `az`/`gh`.
- L'authentification ne doit jamais être enregistrée dans un dépôt, une Activity, une PR ni la configuration partagée.
