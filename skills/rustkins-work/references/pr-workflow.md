# PR GitHub et Azure Boards

Lis ce guide lorsque tu prépares une PR, modifies ses mentions Azure ou traites une review. Les sources de gouvernance sont `RustkinsDocs/docs/project-management/agent-workflow.md` et `definition-of-done-and-tests.md` ; le skill [rustkins-boards](../../rustkins-boards/SKILL.md) fournit les lectures et mutations Azure. Utilise le [modèle de corps](../assets/pr-body.md).

## Retrouver le travail avant de créer

Vérifie le remote et la branche par défaut avec `git remote -v`, `git status --short` et `gh repo view --json defaultBranchRef`. Cherche une PR par branche (`gh pr list --state all --head <branche> --json number,state,headRefName,author,url`) et par auteur, puis compare l'objectif et les commits. Une PR existante liée au même travail se reprend ; un timeout de `gh pr create` exige cette recherche avant tout nouvel essai. N'interprète pas une Activity terminée comme une PR ou une Task terminée.

## Mentions Azure dans la PR

Une mention `AB#142` dans le **corps** de la PR relie le work item, sans changement d'état. Le titre ou un commentaire GitHub ne suffit pas à créer ce lien. Les transitions documentées s'appliquent à la fusion dans la **branche par défaut** ; elles peuvent échouer si l'état ou la connexion Azure ne le permet pas. [Microsoft Learn — liens et transitions GitHub](https://learn.microsoft.com/en-us/azure/devops/boards/github/link-to-from-github?view=azure-devops).

| Cas | Lignes du corps, après lecture des IDs réels | Condition |
| --- | --- | --- |
| PR intermédiaire d'une US | `AB#<us>` puis une ligne `Closed AB#<task>` pour chaque Task réellement finie par cette PR | La DoD de chaque Task et sa review/merge restent à vérifier ; l'US reste à résoudre. |
| PR finale d'une US | `AB#<us>` puis `Closed AB#<task>` pour les dernières Tasks | Choix prudent lorsque l'E2E, la plateforme de test ou les PR précédentes ne sont pas encore prouvés. |
| PR finale avec résolution possible | `Resolved AB#<us>` puis `Closed AB#<task>` pour les dernières Tasks | Toutes les autres PR sont déjà mergées ; AC, tests, CI et version en test sont prouvés avant merge ; les dernières Tasks seront clôturées par ce merge. Vérifier l'ordre et les états après merge. |
| Task ou Bug autonome | `Closed AB#<id>` | La PR termine réellement le livrable et sa DoD est satisfaite au merge. |
| Travail sans ID Azure | Aucune mention `AB#` | Suivi par RustkinsActivity seul. |

Une Task qui couvre plusieurs PR reçoit sa ligne `Closed` seulement dans la PR qui l'achève. Chaque work item à fermer reçoit **sa propre ligne** ; une mention en liste après un seul mot-clé ne déclenche pas toutes les transitions. Évite `Fixes AB#...` dans les commits et le corps lorsqu'aucune transition n'est voulue. Si la validation de test ne peut être faite qu'après merge, garde l'US liée par `AB#` et demande sa transition à `Resolved` via Boards seulement après preuves réelles. `Closed` pour une US attend la Sprint Review humaine.

## Corps, publication et vérification

Copie le modèle dans un fichier `.md` UTF-8, remplis ses sections et retire les commentaires et emplacements inutiles. Pour une US, indique les preuves par AC et par catégorie de test, la révision réellement testée, les checks CI et le déploiement de test ; une absence reste explicitement « à faire ». Pour une Task/Bug autonome, garde les preuves pertinentes. Le corps doit décrire le livrable, les tests exécutés, les limites et les dépendances de merge.

Passe ce fichier à `gh pr create --body-file <chemin>` ou `gh pr edit <numéro> --body-file <chemin>`. Après écriture, récupère `gh pr view <numéro> --json body,state,isDraft,headRefOid,baseRefName,url`, compare le champ `body` au fichier UTF-8 en normalisant seulement CRLF/LF et la fin de fichier, puis vérifie les mentions `AB#` dans le corps distant. Le modèle est un point de départ, jamais un contenu à publier avec ses emplacements.

Sous PowerShell, lis le JSON structuré avec `(gh pr view <numéro> --json body | ConvertFrom-Json).body`. Ne réécris pas le fichier à partir de `gh pr view --json body --jq .body` : PowerShell peut convertir cette sortie en tableau de lignes puis les joindre avec des espaces. Pour contrôler les sauts de ligne après publication :

```powershell
$source = [System.IO.File]::ReadAllText($bodyFile, [System.Text.Encoding]::UTF8)
$published = (gh pr view $prNumber --json body | ConvertFrom-Json).body
if ($LASTEXITCODE -ne 0) { throw 'Lecture de la PR échouée' }
$expected = $source.Replace("`r`n", "`n").TrimEnd([char]10)
$actual = $published.Replace("`r`n", "`n").TrimEnd([char]10)
if ($actual -cne $expected) { throw 'Le Markdown publié diffère du fichier source' }
```

Conserve le fichier source si la comparaison échoue et inspecte aussi le rendu GitHub.

Consulte `gh pr checks <numéro>` et les reviews. Un contrôle GitHub absent n'est pas un contrôle vert. Pour une review, lis le fil en ligne, vérifie le constat, corrige si fondé, teste, pousse sur la même PR, réponds et résous le fil traité. Une remarque non pertinente reçoit une réponse factuelle ; un sujet nécessitant une décision humaine reste visible. Si une PR a été créée malgré un timeout de la commande, retrouve-la par sa branche avant de relancer `gh pr create`.

## Après merge humain

Relis la PR mergée, les états `System.State` de chaque Task et de l'US, et les preuves de la révision effectivement intégrée. L'intégration GitHub ↔ Azure ne valide pas la DoD et peut ignorer une transition interdite. Une Task encore ouverte ou une US non `Resolved` demande une action explicite selon `rustkins-boards`, sans présumer que la syntaxe de la PR a suffi. L'Activity suit le résultat réel de l'intervention, indépendamment de ces états.
