# Lecture et application du planning

Utilise l'organisation et le projet de `~/.rustkins-skills/config.json` explicitement dans chaque commande. Identifie l'équipe avec `az devops team list --org <url> --project <projet> -o json`, puis lis ses sprints avec `az boards iteration team list --team <équipe> --org <url> --project <projet> -o json`. Ce dernier `path` correspond à `System.IterationPath`. `az boards iteration project list` sert à inspecter les nœuds du projet, mais son `path` contient le segment technique `\\Iteration` et ne doit pas être copié tel quel dans un work item. Lis `startDate`/`finishDate` ; si elles sont nulles, signale que les dates du sprint ne sont pas configurées. La racine du projet n'est pas un sprint.

Pour obtenir les US d'un sprint ou du backlog, lance un WIQL borné au projet, par exemple :

```powershell
az boards query --wiql "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'Rustkins' AND [System.WorkItemType] = 'User Story' AND [System.IterationPath] = 'Rustkins\Sprint 1'" --org https://dev.azure.com/Rustkins --project Rustkins -o json
az boards work-item show --id 142 --org https://dev.azure.com/Rustkins --expand all -o json
```

Les valeurs sont illustratives. Adapte le WIQL au projet réel, échappe les apostrophes par deux apostrophes et relis **chaque ID** : la requête seule ne donne pas les AC, SP, parents, dépendances ou responsable. Pour le Product Backlog, consulte aussi l'ordre/stack rank réel plutôt que de trier seulement par ID. Ne prends pas une absence de SP ou de disponibilité pour zéro.

Après validation humaine du Goal, des US retenues, du sprint et des Tasks :

```powershell
python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" set-iteration --id 142 --expected Rustkins --to 'Rustkins\Sprint 1' --reason 'Sprint Planning valide le 2026-11-08 : US 142 retenue'
python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" set-task-iteration --id 151 --parent-id 142 --expected Rustkins --to 'Rustkins\Sprint 1' --reason 'Task 151 incluse dans le planning valide'
python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" create-task --input .\task-142.json
```

Le fichier Task suit le [contrat Boards](../../rustkins-boards/references/az-workflow.md) (`parent_id`, `title`, `deliverable`, `done_criteria`). Place-le hors dépôt ou dans un brouillon ignoré. Sous Claude Code, utilise le même chemin frère sous `$HOME/.claude/skills/`. `set-iteration` refuse une US d'un autre type/projet, un ancien chemin différent et une cible hors du projet ; `set-task-iteration` exige une Task inachevée réellement enfant de cette US et vérifie que l'US est déjà dans le sprint cible. Azure valide l'existence du chemin. Si une Task est déjà dans un autre sprint que l'US, analyse ce cas avant de la déplacer. La proposition approuvée distingue US nouvelles, reportées et non retenues ainsi que les Tasks existantes à suivre. L'ajout ou le retrait pendant le sprint exige une nouvelle décision de Timothy.
