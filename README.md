# RustkinsSkills

Skills partagés par Codex et Claude Code pour les dépôts Rustkins. [`rustkins-activity`](skills/rustkins-activity/SKILL.md) gère le journal d'intervention au moyen de la CLI Rust de [RustkinsActivity](https://github.com/Rustkins-Project/RustkinsActivity). [`rustkins-boards`](skills/rustkins-boards/SKILL.md) consulte et tient à jour Azure Boards. [`rustkins-work`](skills/rustkins-work/SKILL.md) conduit les développements jusqu'à la PR. [`rustkins-ask-team`](skills/rustkins-ask-team/SKILL.md) prépare des questions à l'équipe et récupère leurs réponses validées. L'installateur découvre automatiquement les dossiers `skills/*/SKILL.md` et copie leurs ressources dans les deux clients.

Les deux agents reçoivent **les mêmes instructions**, le même profil humain, le même clone RustkinsActivity et le même dossier de brouillons. La recherche contextuelle et les décisions de reprise sont dans le skill ; le format, la validation, les opérations ciblées, le verrou et Git restent dans RustkinsActivity. Les règles transverses Azure sont dans RustkinsDocs.

## Roadmap des skills

Les quatre premiers skills sont disponibles. Les autres sont **spécifiés mais pas encore disponibles** ; ne pas supposer qu'ils sont installés ou testés.

| Premier lot | Objectif |
| --- | --- |
| `rustkins-activity` (existant) | Journal Git via la CLI RustkinsActivity |
| `rustkins-boards` (disponible) | Azure Boards via `az` ; Tasks, US, Bugs, états, relations, DoR/DoD |
| `rustkins-work` (disponible) | Développement autonome jusqu'à la PR ; Git/`gh`, tests, review humaine |
| `rustkins-ask-team` (disponible) | Questions et réponses validées via l'API privée RustkinsDiscordBot |
| `rustkins-knowledge` (à créer) | Recherche/contribution à RustkinsDocs, ADR proposées par PR |

Ensuite : `rustkins-sprint-planning`, `rustkins-sprint-status` et `rustkins-sprint-close`.

**Dossiers de conception :** [architecture](docs/architecture.md), [plan d'implémentation](docs/implementation-plan.md), [installation et qualité UTF-8](docs/installation-and-quality.md) et [contrats de chaque skill](docs/skills/). Les comportements sont soumis à la gouvernance de RustkinsDocs, notamment les critères de Sprint Review.

Choix structurants : `gh` et `az` en priorité ; API directe seulement lorsque pertinente (notamment Discord) ; **pas de dépendance à RustkinsMCP**, pas de versionnement individuel des skills, et français/Unicode pris en charge dans tous les scripts. La review et le merge des PR restent humains.

## Prérequis

- Python 3 pour l'installateur. Chaque skill peut déclarer ses propres outils dans `requirements.json`.
- Pour `rustkins-activity` : Git, Rust/Cargo et un clone RustkinsActivity à jour, sur `main`, avec les commandes `discover`, `prepare-create` et `prepare-patch`.
- Pour `rustkins-boards` : Azure CLI avec l'extension `azure-devops`, accès au projet Azure et configuration `--azure-organization` / `--azure-project`.
- Pour `rustkins-work` : Git et GitHub CLI authentifié ; Azure CLI et le projet configuré si le travail concerne un work item.
- Pour `rustkins-ask-team` : URL HTTPS du bot dans `discord.base_url` et jeton client IA du développeur dans `RUSTKINS_DISCORD_AI_TOKEN` lors de l'envoi ou de la lecture.
- `user.name` et `user.email` Git configurés dans ce clone. La CLI `setup` active le hook pré-commit sans écraser un hook incompatible.

## Installation Windows et Linux

Cloner ce dépôt et RustkinsActivity. Depuis le dossier RustkinsSkills, lancer selon la machine `python install.py` (Windows) ou `python3 install.py` (Linux) avec les paramètres ci-dessous. Chaque développeur fournit son **propre** profil et login GitHub ; ne pas utiliser le nom de l'agent comme auteur.

```text
python install.py --profile Timothy --author <login-GitHub> --activity-clone <chemin-RustkinsActivity> --drafts-dir <dossier-persistant-hors-clone>
```

Remplacer `Timothy` par `Alexis` ou `Loick` selon le poste. L'installateur crée `~/.rustkins-skills/config.json`, active le hook du clone Activity, copie chaque skill disponible vers `~/.codex/skills/<nom>` et `~/.claude/skills/<nom>`, et installe les helpers communs sous `~/.rustkins-skills/shared/`. Le dossier de brouillons reste hors clone et n'est jamais effacé par l'installateur. Relancer les clients si leurs skills sont chargés au démarrage.

Les champs `--docs-clone`, `--azure-organization`, `--azure-project` et `--discord-base-url` sont facultatifs à l'installation. Ils alimentent respectivement `docs_clone`, `azure.organization`, `azure.project` et `discord.base_url` dans le même JSON UTF-8. Les deux options Azure sont nécessaires pour utiliser `rustkins-boards`. Ne pas y placer de token ou de PAT. Les clés déjà présentes sont conservées si leurs options ne sont pas fournies.

## Mise à jour

Mettre à jour le clone RustkinsSkills avec `git pull --ff-only`, puis relancer `python install.py` ou `python3 install.py` **sans arguments**. Les réglages existants sont conservés ; pour changer une valeur, repasser uniquement son option. Une copie installée identique est laissée en place. Si son contenu change, l'ancien dossier est conservé dans `~/.codex/skills/.rustkins-backups/<identifiant>/<skill>` ou `~/.claude/skills/.rustkins-backups/<identifiant>/<skill>`, sur le même volume que la destination. Les sauvegardes créées par une version précédente sous `~/.rustkins-skills/backups/` restent en place. Vérifier ces sauvegardes avant de les supprimer manuellement.

Un skill dont les prérequis manquent est signalé et ignoré ; les autres sont installés. La commande retourne alors un code non nul. L'installateur prépare toutes les copies avant remplacement et restaure les anciens dossiers si un remplacement échoue.

## Diagnostic et ajout d'un skill

Lancer `python install.py --check` (ou `python3` sous Linux) pour vérifier les outils déclarés et la configuration Activity sans installer. Cette vérification ne lance pas `setup` et ne valide pas les connexions distantes. En cas d'erreur, lire le diagnostic du skill, puis vérifier les droits d'écriture de `~/.codex/skills`, `~/.claude/skills` et `~/.rustkins-skills`. Après une interruption, relancer l'installation ; les copies précédentes sous `.rustkins-backups/` permettent une restauration manuelle.

Pour ajouter un skill, créer `skills/<nom>/SKILL.md` et placer ses ressources relatives dans ce dossier. Un fichier facultatif `requirements.json` peut déclarer `{"commands": ["git", "gh"]}` ou `{"commands": ["az"], "azure_devops_extension": true}`. L'installateur copie le dossier entier sans modification de son code. L'authentification et les permissions restent à contrôler lors de l'utilisation du skill.

## Socle CLI et UTF-8

Le module [`shared/cli_utf8.py`](shared/cli_utf8.py) est installé une seule fois sous `~/.rustkins-skills/shared/`, utilisable par les scripts des futurs skills. Il fournit `run_cli` et `run_json` pour `az` et `gh` avec liste d'arguments, sans shell, sortie UTF-8 stricte et délai contrôlé ; `read_utf8`, `write_utf8`, `read_json` et `write_json` pour les fichiers ; `plain_text_to_html` pour un champ HTML issu de texte brut ; et `temporary_markdown` pour un fichier UTF-8 fermé avant `gh --body-file`.

Pour créer **ou modifier** une description de PR sous PowerShell, suivre la [procédure de conservation du Markdown](docs/installation-and-quality.md#corps-de-pr-multiligne-dans-powershell) et comparer le corps publié au fichier source.

Un script installé peut importer ce module ainsi :

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".rustkins-skills" / "shared"))
from cli_utf8 import run_cli, run_json, temporary_markdown
```

Les exceptions `CliError` indiquent l'outil et la catégorie d'échec sans reproduire les arguments, la sortie ou l'environnement, qui peuvent contenir des secrets. Après un échec ou un timeout d'une commande de mutation, relire l'état distant avant toute nouvelle tentative. Le module ne gère ni l'authentification, ni les décisions métier, ni les retries.

## Utilisation

Lors d'un travail sur Rustkins, le skill doit être sélectionné automatiquement. Pour un premier essai explicite, utiliser `$rustkins-activity` dans Codex ou `/rustkins-activity` dans Claude Code. Le skill lit le profil configuré, récupère les transactions en attente, recherche brouillons et activités ouvertes, puis choisit la reprise ou la création. Une ambiguïté réelle nécessite la décision humaine. La CLI réalise la préparation et publication ; aucun Git manuel n'est nécessaire pour les fiches d'activité.

Les exemples JSON et la liste des commandes se trouvent dans [le contrat CLI](skills/rustkins-activity/references/cli-workflow.md). Les garanties du moteur Rust (validation, brouillons, publication et reprise) sont décrites dans [RustkinsActivity](https://github.com/Rustkins-Project/RustkinsActivity#documentation-de-référence).

Pour Azure Boards, invoquer `$rustkins-boards` dans Codex ou `/rustkins-boards` dans Claude Code. Le [guide Azure](skills/rustkins-boards/references/az-workflow.md) montre la recherche, la création/reprise d'une Task, son attribution et ses transitions d'avancement. Les tests automatisés simulent le CLI ; ils ne modifient pas le backlog réel.

Pour réaliser ou reprendre un développement, une Task, un Bug ou une review, invoquer `$rustkins-work` dans Codex ou `/rustkins-work` dans Claude Code. Le [guide PR](skills/rustkins-work/references/pr-workflow.md) précise la reprise d'une branche, les mentions Azure et la vérification du corps publié ; le [modèle de corps](skills/rustkins-work/assets/pr-body.md) sert de point de départ. Le skill coordonne Activity et Boards selon le contexte et s'arrête à une PR normale ; review et merge restent humains.

Pour consulter l'équipe sur une décision manquante, invoquer `$rustkins-ask-team` dans Codex ou `/rustkins-ask-team` dans Claude Code. Le [guide des questions](skills/rustkins-ask-team/references/questions-workflow.md) décrit le fichier d'entrée, la préparation durable avant POST, la reprise après timeout et la lecture des seules réponses validées. Les tests du client simulent le bot ; aucune question réelle n'est créée pendant la recette automatisée.

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
