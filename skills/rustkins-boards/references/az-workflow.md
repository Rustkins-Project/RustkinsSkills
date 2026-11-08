# Workflow Azure Boards

## Préflight et lecture

Le skill est disponible après `python install.py` si `az` et l'extension `azure-devops` sont présents. Configure `azure.organization` et `azure.project` via `python install.py --azure-organization https://dev.azure.com/<organisation> --azure-project <projet>` ; cette configuration locale ne stocke pas de secret. Authentifie `az` séparément avec la méthode de ton organisation.

Exemples PowerShell (remplacer les valeurs ; conserver les arguments séparés) :

```powershell
az extension show --name azure-devops -o json
az boards work-item show --id 142 --org https://dev.azure.com/organisation --expand all -o json
az boards query --wiql "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'Rustkins' AND [System.WorkItemType] = 'User Story'" --org https://dev.azure.com/organisation --project Rustkins -o json
az boards work-item relation show --id 142 --org https://dev.azure.com/organisation -o json
```

Les champs utiles incluent `System.WorkItemType`, `System.Title`, `System.Description`, `Microsoft.VSTS.Common.AcceptanceCriteria`, `System.State`, `System.AssignedTo`, `System.IterationPath`, `System.AreaPath`, `System.Parent` et `relations`. Les relations `System.LinkTypes.Hierarchy-Reverse/Forward` portent la hiérarchie. Inspecte les autres relations pour dépendances et liens GitHub avant d'en déduire une cause ou une livraison. Le WIQL renvoie des IDs, pas le détail complet ; échappe une apostrophe littérale par deux apostrophes et borne toujours la requête au projet. Pour les filtres d'itération, état ou responsable, vérifie les chemins/noms réels du projet.

## Task contrôlée

Prépare un fichier JSON UTF-8, par exemple :

```json
{
  "parent_id": 142,
  "title": "Implémenter la validation du formulaire",
  "deliverable": "Le formulaire valide les champs obligatoires et affiche les erreurs utiles.",
  "done_criteria": [
    "Les règles couvrent les cas valides et invalides.",
    "Les tests pertinents passent."
  ]
}
```

```powershell
python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" create-task --input .\task.json
python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" claim-task --id 151 --identity developpeur@example.org
python -X utf8 "$HOME/.codex/skills/rustkins-boards/scripts/boards_ops.py" set-progress --id 151 --expected New --to Active --reason "Développement démarré"
```

Pour le Sprint Planning ou report validé, `set-iteration --id <US> --expected <chemin-lu> --to <sprint-vérifié> --reason <décision>` protège la révision et relit l'itération. `set-task-iteration --id <Task> --parent-id <US> --expected <chemin-lu> --to <sprint-vérifié> --reason <décision>` fait de même pour chaque Task enfant inachevée approuvée ; une Task `Closed` reste dans son itération historique. La racine du projet n'est pas un sprint ; vérifie le chemin cible dans `az boards iteration team list --team <équipe>` (le chemin de `iteration project list` contient un segment technique supplémentaire). Pour une décision humaine de Sprint Review, `review-story --input <decision.json>` applique `accepted` (`Resolved → Closed`) ou `rejected` (`Resolved → Active`) avec date, participants, sprint, URL du compte rendu et motif. Lis le [parcours de clôture](../../rustkins-sprint-close/references/close-workflow.md). Le script ne décide ni de la DoD ni de la sélection du sprint.

Le script appelle le CLI Azure sans shell, écrit le texte brut sous forme HTML échappé et vérifie les objets distants. Il refuse les doublons ambigus, les réaffectations et les changements d'état concurrents. Il utilise une opération REST JSON Patch via `az rest` avec `test /rev` avant les champs modifiés ; une session `az login` est nécessaire pour le jeton Microsoft Entra Azure DevOps. L'extension `az devops invoke` 1.0.10 résout `workItems` vers la route de création (`${type}`) sur le projet Test : elle ne convient donc pas à ce PATCH par ID. Une perte de réponse après effet distant exige une relecture ; l'absence de confirmation n'autorise pas une nouvelle création. Il n'y a pas de verrou d'unicité côté Azure : deux créations réellement simultanées restent possibles et doivent être rapprochées manuellement.

Pour les autres mutations (relations de dépendance, Bug/Issue, Task sans PR, US `Resolved`), lis l'état juste avant, respecte la gouvernance du [skill](../SKILL.md), applique une opération explicite avec garde de révision si disponible, relis ensuite. `az boards work-item update` n'offre pas de garde de révision ; ne l'utilise pas pour écraser une attribution ou un état observé précédemment. N'écris jamais seulement `System.BoardColumn`. Ne ferme jamais une US sans décision humaine de Sprint Review.

## Références

- [Azure CLI : work-item](https://learn.microsoft.com/en-us/cli/azure/boards/work-item?view=azure-cli-latest)
- [Azure CLI : query](https://learn.microsoft.com/en-us/cli/azure/boards?view=azure-cli-latest)
- [Azure CLI : relations](https://learn.microsoft.com/en-us/cli/azure/boards/work-item/relation?view=azure-cli-latest)
- [Azure CLI : rest](https://learn.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest#az-rest)
- [REST Work Items Update et JSON Patch](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.1)
- [Gouvernance RustkinsDocs](https://github.com/Rustkins-Project/RustkinsDocs/tree/main/docs/project-management)
