# RustkinsSkills

Skills partagés par Codex et Claude Code pour les dépôts Rustkins. Le premier skill, [`rustkins-activity`](skills/rustkins-activity/SKILL.md), gère le journal d'intervention au moyen de la CLI Rust de [RustkinsActivity](https://github.com/Rustkins-Project/RustkinsActivity). Le dépôt peut accueillir d'autres dossiers sous `skills/` sans modifier ce workflow.

Les deux agents reçoivent **les mêmes instructions**, le même profil humain, le même clone RustkinsActivity et le même dossier de brouillons. La recherche contextuelle et les décisions de reprise sont dans le skill ; le format, la validation, les opérations ciblées, le verrou et Git restent dans RustkinsActivity. Les règles transverses Azure sont dans RustkinsDocs.

## Roadmap des skills (conception, non encore implémentée)

Le dépôt contient aujourd'hui seulement le skill opérationnel `rustkins-activity`. Les autres skills ci-dessous sont **spécifiés mais pas encore disponibles** ; ne pas supposer qu'ils sont installés ou testés.

| Premier lot | Objectif |
| --- | --- |
| `rustkins-activity` (existant) | Journal Git via la CLI RustkinsActivity |
| `rustkins-boards` (à créer) | Azure Boards via `az` ; Tasks, US, Bugs, états, relations, DoR/DoD |
| `rustkins-work` (à créer) | Développement autonome jusqu'à la PR ; Git/`gh`, tests, review humaine |
| `rustkins-ask-team` (à créer) | Questions et réponses validées via l'API privée RustkinsDiscordBot |
| `rustkins-knowledge` (à créer) | Recherche/contribution à RustkinsDocs, ADR proposées par PR |

Ensuite : `rustkins-sprint-planning`, `rustkins-sprint-status` et `rustkins-sprint-close`.

**Dossiers de conception :** [architecture](docs/architecture.md), [plan d'implémentation](docs/implementation-plan.md), [installation et qualité UTF-8](docs/installation-and-quality.md) et [contrats de chaque skill](docs/skills/). Les comportements sont soumis à la gouvernance de RustkinsDocs, notamment les critères de Sprint Review.

Choix structurants : `gh` et `az` en priorité ; API directe seulement lorsque pertinente (notamment Discord) ; **pas de dépendance à RustkinsMCP**, pas de versionnement individuel des skills, et français/Unicode pris en charge dans tous les scripts. La review et le merge des PR restent humains.

## Prérequis

- Python 3 et Rust/Cargo, plus Git avec accès à `Rustkins-Project/RustkinsActivity`.
- Un clone RustkinsActivity à jour par développeur, sur `main`, avec les commandes `discover`, `prepare-create`, `prepare-patch`, `publish` et `recover`.
- `user.name` et `user.email` Git configurés dans ce clone. La CLI `setup` active le hook pré-commit sans écraser un hook incompatible.

## Installation Windows et Linux

Cloner ce dépôt et RustkinsActivity. Depuis le dossier RustkinsSkills, lancer selon la machine `python install.py` (Windows) ou `python3 install.py` (Linux) avec les paramètres ci-dessous. Chaque développeur fournit son **propre** profil et login GitHub ; ne pas utiliser le nom de l'agent comme auteur.

```text
python install.py --profile Timothy --author <login-GitHub> --activity-clone <chemin-RustkinsActivity> --drafts-dir <dossier-persistant-hors-clone>
```

Remplacer `Timothy` par `Alexis` ou `Loick` selon le poste. L'installateur crée `~/.rustkins-skills/config.json`, active le hook du clone et copie exactement le même skill vers `~/.codex/skills/rustkins-activity` et `~/.claude/skills/rustkins-activity`. Le dossier de brouillons n'est ni dans le clone ni synchronisé automatiquement. Vérifier que l'agent peut lire ce fichier et exécuter Cargo/Git. Relancer les agents après installation si leurs skills ont été chargés au démarrage.

## Mise à jour

Mettre à jour les clones par la procédure Git habituelle, puis relancer `python install.py` ou `python3 install.py` **sans arguments** depuis RustkinsSkills. Le fichier de configuration existant conserve le profil, le login et les chemins. Pour changer une valeur, repasser uniquement son option. L'installateur remplace les copies installées du skill ; conserver les modifications locales dans ce dépôt source.

## Utilisation

Lors d'un travail sur Rustkins, le skill doit être sélectionné automatiquement. Pour un premier essai explicite, utiliser `$rustkins-activity` dans Codex ou `/rustkins-activity` dans Claude Code. Le skill lit le profil configuré, récupère les transactions en attente, recherche brouillons et activités ouvertes, puis choisit la reprise ou la création. Une ambiguïté réelle nécessite la décision humaine. La CLI réalise la préparation et publication ; aucun Git manuel n'est nécessaire pour les fiches d'activité.

Les exemples JSON et la liste des commandes se trouvent dans [le contrat CLI](skills/rustkins-activity/references/cli-workflow.md). Les garanties du moteur Rust (validation, brouillons, publication et reprise) sont décrites dans [RustkinsActivity](https://github.com/Rustkins-Project/RustkinsActivity#documentation-de-référence).

## Vérification après installation

Exécuter les tests du dépôt des skills, puis ceux de la CLI Rust (chaque commande depuis le dépôt correspondant) :

```bash
python -m unittest discover -s tests -v
cargo test
cargo run -- validate
```

Pour la recette fonctionnelle, utiliser **un remote Git de test isolé**, ou une véritable intervention autorisée à journaliser (éviter les fausses fiches dans le journal officiel, car les activités clôturées sont immuables). Demander à Codex de créer puis publier une activité, vérifier sa présence sur `origin/main`, la faire reprendre par Claude Code sur le même poste, puis la clôturer. Contrôler les références de PR et le résumé Discord si ce flux est configuré. Vérifier une erreur de publication en conservant le même `operation_id` et en utilisant `recover` ; ne pas créer de doublon.

Les tests unitaires d'installation couvrent la configuration commune aux deux clients ; les tests de Git et du format d'activité appartiennent au dépôt RustkinsActivity. L'absence de preuve de recette sur un autre poste ne doit pas être présentée comme un test réussi.

## Répartition des responsabilités

- **RustkinsSkills** : installer les instructions des agents et leurs paramètres locaux.
- **RustkinsActivity** : valider, préparer, publier et récupérer une intervention.
- **RustkinsDocs** : gouvernance et lien avec Azure Boards.
- **RustkinsDiscordBot** : lecture quotidienne des fiches publiées, sans écriture dans le journal.

Les résultats historiques des premières vérifications restent consultables dans l'historique Git ; les commandes et scénarios ci-dessus constituent désormais la référence maintenue.
