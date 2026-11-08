---
name: rustkins-sprint-status
description: Produit un état factuel du sprint Rustkins à partir des états Azure, dépendances, PR et CI GitHub, sans compter les US Resolved comme livrées.
---

# État du sprint Rustkins

Utilise ce skill pour un point de sprint à la demande ; aucun Daily ni suivi permanent n'est implicite. Lis la [méthode de collecte et de calcul](references/status-workflow.md). La gouvernance approuvée est `RustkinsDocs/docs/project-management/sprint-process.md` (DOC-0028), `states-and-dependencies.md` et `definition-of-done-and-tests.md`. Utilise `rustkins-boards` pour les champs Azure et `rustkins-work` pour la lecture des PR/CI ; `RustkinsActivity` peut apporter du contexte, jamais remplacer les états Azure.

1. Vérifie l'organisation, le projet, l'authentification et le **chemin d'itération exact**. Note l'heure du constat. Interroge toutes les US de cette itération et relis chacune avec `--expand all` ; lis ses Tasks, Bugs, dépendances, états `System.State`, SP et responsable. Une colonne de Board ne remplace pas l'état.
2. Pour les repos réellement liés, lis les PR ouvertes/fusionnées et les checks de la révision concernée avec `gh`. Distingue PR fusionnée, CI verte, version déployée et E2E sur la plateforme de test : ce sont quatre preuves différentes. Si une relation PR, un run ou une plateforme manque, marque la preuve « inconnue » ou « absente » selon ce que tu as vérifié.
3. Rapporte le nombre d'US par état, les Tasks `Active`, `Blocked` et `On Hold`, les dépendances et prochaines actions. Additionne les SP engagés **uniquement lorsqu'ils sont connus** ; compte comme livrés seulement les SP des US réellement `Closed` après Sprint Review. Une US `Resolved` attend la review et ne contribue pas aux SP livrés. N'attribue pas les inconnus à zéro.
4. Propose les décisions utiles à Timothy et à l'équipe, sans modifier le Sprint Goal, l'engagement, la priorité ou un work item pendant ce rapport. Rattache chaque constat important à son ID/lien Azure et, si pertinent, à la PR et au run CI.

Le résultat est un instantané daté ; un statut GitHub ou Azure peut changer après la lecture. Les disponibilités humaines restent celles déclarées, sans inférence depuis une absence d'activité.
