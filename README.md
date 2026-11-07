# RustkinsSkills

Skills partagés par Codex et Claude Code pour les dépôts Rustkins. Le premier skill, [`rustkins-activity`](skills/rustkins-activity/SKILL.md), gère le journal d'intervention au moyen de la CLI Rust de [RustkinsActivity](https://github.com/Rustkins-Project/RustkinsActivity). Le dépôt peut accueillir d'autres dossiers sous `skills/` sans modifier ce workflow.

Les deux agents reçoivent **les mêmes instructions**, le même profil humain, le même clone RustkinsActivity et le même dossier de brouillons. La recherche contextuelle et les décisions de reprise sont dans le skill ; le format, la validation, les opérations ciblées, le verrou et Git restent dans RustkinsActivity. Les règles transverses Azure sont dans RustkinsDocs.

## Prérequis

- Python 3 et Rust/Cargo, plus Git avec accès à `Rustkins-Project/RustkinsActivity`.
- Un clone RustkinsActivity par développeur, sur `main`, dont la version contient les commandes `discover`, `prepare-create` et `prepare-patch`.
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

Les exemples JSON et la liste des commandes se trouvent dans [le contrat CLI](skills/rustkins-activity/references/cli-workflow.md). Le [rapport de validation](TESTING.md) distingue les tests automatisés des essais d'agents non exécutés.
