# Plan d'implémentation de RustkinsSkills

> **Documents de cadrage uniquement** : aucun skill nouveau, aucun script d'intégration Azure/Discord ni automatisation de sprint ne sont implémentés par cette PR.
> **Principe de livraison :** jalons fonctionnels indépendants, PR de code courtes et revues humaines ; pas de versionnement par skill.

## Hypothèses et prérequis

- Équipe de trois personnes, postes Windows et/ou Linux, Codex ou Claude Code.
- `RustkinsActivity` et son skill actuel restent opérationnels ; aucune réécriture.
- Projet Azure DevOps configuré avec Azure Boards et processus d'états décrit dans RustkinsDocs.
- Azure Boards for GitHub installé sur les repos nécessaires ; `AB#<id>` relie, `Closed AB#<id>` et `Resolved AB#<id>` demandent une transition au merge **sur la branche par défaut**.
- `RustkinsDiscordBot` expose déjà POST/GET `/internal/questions`. Pas de nouvelle API à coder pour le premier lot.
- Aucun composant de `RustkinsMCP` n'est requis.

## Ordre et dépendances

| Étape | Livraison de code attendue | Dépendances | Critère de recette |
| --- | --- | --- | --- |
| **0 — Alignement documentaire** | Faire reviewer/merger les PR de cadrage Skills, Docs et DiscordBot | Aucune | Les textes normatifs ne se contredisent pas ; cas `Resolved` et DoD explicités |
| **1 — Installateur commun** | Détection et installation de tous les dossiers `skills/*`, références, scripts ; configuration persistante ; diagnostics des outils | 0 | Codex et Claude voient les mêmes cinq entrées à terme ; `rustkins-activity` reste fonctionnel |
| **2 — Socle CLI/UTF-8** | Helpers partagés minimaux pour lancer `az`/`gh` sans shell et pour fichiers JSON/HTML/Markdown UTF-8 ; tests Windows/Linux | 1 | Titres et descriptions accentués intacts ; erreurs et sorties JSON exploitables ; aucun secret divulgué |
| **3 — rustkins-boards** | SKILL, références opérationnelles, scripts seulement où utiles | 2 | Recherche, lecture complète des champs et relations, création/reprise Task, attribution à la prise en charge, mutation sûre, DoD |
| **4 — rustkins-work** | SKILL, instructions branches/PR/reviews, template de PR ; coordination Activity/Boards | 3 | Une US existante → Tasks → code/tests → PR ; liens Azure valides ; aucune fusion par agent |
| **5 — rustkins-ask-team** | SKILL + client HTTP local ciblé, durablement reprenable, tests simulés | 2 | Question créée une seule fois, réponse pending/answered, récupération après nouvelle session |
| **6 — rustkins-knowledge** | SKILL, navigation du clone Docs et contribution par PR/ADR | 2 | Recherche sur sources pertinentes, contribution sans doublon, ADR proposée sans auto-approbation |
| **7 — Premier parcours intégré** | Ajustements et tests d'acceptation inter-skills, documentation du poste | 3–6 | Scénarios end-to-end décrits ci-dessous réussis sur données de test |
| **8 — Sprint skills** | `rustkins-sprint-planning`, `rustkins-sprint-status`, `rustkins-sprint-close` (trois PR possibles) | 3,6,7 | Planning validé, suivi fiable, review/rétro et report dans les règles Azure |

Les cinq skills sont le **premier lot fonctionnel** ; les skills de sprint restent explicitement prévus, mais peuvent être développés après la stabilisation des opérations de base.

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

## Organisation des PR de développement

Chaque étape peut être confiée à un agent IA. Sa PR doit contenir : portée précise, fichiers concernés, tests exécutés et résultats réels, captures d'output utiles, risques et dépendances, références Azure si elles existent. Les PR ne sont pas fusionnées par l'agent. Les cas d'acceptation ci-dessus constituent la base des tests, pas une autorisation de modifier RustkinsDocs à volonté.

### Brief réutilisable à donner à l'agent

> Implémente **l'étape N** de `RustkinsSkills/docs/implementation-plan.md`. Lis `docs/architecture.md`, `docs/installation-and-quality.md`, la spécification du skill, et les règles RustkinsDocs pertinentes. Ne développe pas d'autre étape. Préserve `rustkins-activity`, utilise d'abord `gh`, `git` et `az`, réserve les API directes aux cas justifiés, teste le français en UTF-8 sur les plateformes disponibles. Crée une branche et une PR sans merge, avec tests, preuves, limites et références Azure réelles. Si une décision fonctionnelle ou une ADR nouvelle est indispensable, pose la question plutôt que d'inventer l'arbitrage.

## Risques à contrôler

- Conflit entre `Resolved` au merge et les E2E sur plateforme de test : **ne pas atténuer la DoD** pour simplifier les PR.
- Une PR finale créée tôt mais mergée avant une PR intermédiaire : retirera le droit à `Resolved` ; vérifier à nouveau avant le merge.
- L'application Azure Boards peut ignorer une transition invalide ; contrôler `System.State` après merge plutôt que présumer le succès.
- Les APIs/CLI évoluent ; adapter une commande après une petite preuve locale, sans introduire une dépendance au MCP.
- Plusieurs agents ou retries peuvent créer des doublons ; réconciliation par état réel, aucune clé d'idempotence fictive pour `az`/`gh`.
- L'authentification ne doit jamais être enregistrée dans un dépôt, une Activity, une PR ni la configuration partagée.
