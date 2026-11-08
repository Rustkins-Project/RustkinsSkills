# Construire un état de sprint

Confirme le sprint de l'équipe dans `az boards iteration team list --team <équipe> --org <url> --project <projet> -o json` ; trouve le nom d'équipe via `az devops team list` si nécessaire. Utilise le `path` de l'équipe comme `System.IterationPath`, et non le `path` de classification de `az boards iteration project list`, qui contient `\\Iteration`. Interroge les US par `System.TeamProject`, `System.WorkItemType = 'User Story'` et `System.IterationPath = '<chemin exact>'` ; double les apostrophes littérales en WIQL. La réponse de `az boards query` fournit des IDs : `az boards work-item show --id <id> --org <url> --expand all -o json` est nécessaire pour chaque US et enfant.

Vérifie les liens Parent/Child, les dépendances, `System.State`, `System.AssignedTo`, `Microsoft.VSTS.Scheduling.StoryPoints` et les champs de date pertinents. Pour un SP absent, écris « inconnu » et donne aussi le nombre d'US sans estimation ; ne publie pas un total prétendument complet. Pour les dépendances, indique le sens du lien et l'état de l'autre extrémité.

Pour chaque PR identifiée par une relation Azure ou les références de l'US :

```powershell
gh pr view <numero> -R <organisation/depot> --json state,mergedAt,headRefOid,baseRefName,url
gh pr checks <numero> -R <organisation/depot>
```

Si le dépôt ou la PR ne peut être identifié sans ambiguïté, dis-le ; ne construis pas un lien depuis un titre. Une CI verte sur une PR ne prouve ni le déploiement ni un E2E sur la révision déployée.

Structure conseillée du rapport : sprint/chemin/date ; Goal approuvé ; US par état ; SP engagés (connus + inconnus) ; SP livrés (`Closed` seulement) ; Tasks actives/bloquées/en pause ; PR/CI et preuves de test ; dépendances/risques ; décisions demandées. Les US `Resolved` apparaissent séparément comme prêtes à la review, pas dans les livrées.
