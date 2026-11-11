---
name: rustkins-activity
description: Journalise automatiquement les interventions de développement Rustkins avec la CLI RustkinsActivity, lors d'une création, reprise, progression, publication ou clôture, sous Codex ou Claude Code.
---

# Journal RustkinsActivity

Applique ce workflow lorsque tu interviens sur un dépôt Rustkins. Le même skill et la même configuration sont installés pour Codex et Claude Code. Le lanceur et la CLI lisent `~/.rustkins-skills/config.json` : `profile` et `author` identifient le développeur humain. Dans le JSON de création, fournis `agent` (`codex` ou `claude-code`) ; la CLI renseigne `profile` et `author`. Ne change jamais ces champs sur une activité reprise.

La source de vérité métier est `RustkinsActivity/docs/activity-workflow.md`. La CLI du clone configuré possède la validation, la préparation durable, la publication Git et la récupération. Depuis n'importe quel dossier, exécute `python "$HOME/.rustkins-skills/shared/activity.py" <commande>` sous PowerShell ou `python3 "$HOME/.rustkins-skills/shared/activity.py" <commande>` sous Linux. Utilise ce lanceur pour obtenir le clone et les valeurs locales configurées. Ne rédige jamais directement sous `activities/` et ne publie jamais ces fiches avec tes propres commandes Git.

## Avant le travail

1. Détermine l'intervention cohérente, son objectif et sa condition de fin. Repère tous les dépôts Rustkins effectivement concernés à partir des dépôts Git du travail, sous forme `owner/repo`. Une intervention peut avoir plusieurs dépôts et plusieurs PR. Ne déduis pas un ticket Azure du seul sujet.
2. Lance `recover` pour les transactions interrompues. En cas d'erreur, conserve les brouillons et résous la cause avant de préparer une autre opération.
3. Lance `discover`. Cette commande lit les brouillons du poste et récupère les fiches de `origin/main` pour le profil configuré, sans modifier le working tree. Si elle échoue, ne crée pas à l'aveugle : rétablis l'accès ou explique le blocage.
4. Examine d'abord les brouillons non publiés, puis les activités `in_progress`, `paused` ou `blocked` du profil. Compare ID explicite, objectif et condition de fin, périmètre, dépôts, contexte récent, work item et PR. Même dépôt ou même ticket ne suffit pas. Reprends **sans demander** une correspondance claire, y compris créée par l'autre agent. Plusieurs correspondances crédibles exigent une seule question ciblée. Une activité `completed` ou `abandoned` sert seulement de contexte ; pour un travail de review ultérieur, crée une nouvelle activité et référence l'ancienne dans le résumé ou le journal.
5. Si aucune correspondance n'existe, prépare puis publie une activité. Pour un travail significatif, fais-le au démarrage en `in_progress`. Pour une intervention courte déjà accomplie, une création directe en `completed` est possible avec dates, résultat et vérifications réels.

## Préparer et publier

Les commandes `prepare-create --input <json>` et `prepare-patch --input <json>` prennent des fichiers JSON temporaires. La première accepte `CreateInput` sans `profile` ni `author` ; la CLI les ajoute depuis la configuration. La seconde accepte `{ "path": "activities/.../<id>.md", "changes": [...] }`. Consulte [le contrat CLI](references/cli-workflow.md) pour les champs et exemples. La sortie contient `operation_id`. Garde cet ID pour les retries ; **ne prépare pas une nouvelle opération pour réessayer**. La CLI prévalide et conserve le brouillon hors clone.

Lance `publish <operation_id>`. Seule sa confirmation sur `origin/main` vaut publication. Si l'appel échoue, lance `recover`, puis `discover` pour inspecter l'état ; réessaie le même ID quand c'est sûr. Un brouillon `needs_resolution` demande de corriger l'intention ou d'arbitrer le conflit, sans écraser la fiche ni effacer le brouillon.

Pour un patch, utilise les `path`, sections et empreintes `sha256` renvoyés par `discover`. Ajoute un dépôt via `add_repository`, une PR ou un document connu via `add_reference`, et un événement utile via `append_journal`. Si un work item Azure existant et pertinent est connu, renseigne `work_item_id` avec `set_metadata` et sa valeur courante comme `expected`. Mets à jour le Résumé et le Journal dans **un même patch** lors d'un changement d'objectif. Pour une clôture, mets le résultat, les vérifications et `set_status` dans **un même patch**. Les transitions depuis `paused` ou `blocked` doivent refléter une reprise effective ou un déblocage vérifié.

Journalise les étapes significatives, blocages, décisions et vérifications réelles, sans transcription privée ni secret. La fin de session IA ne termine jamais l'activité. Passe à `completed` quand la condition de fin est satisfaite et le livrable attendu publié ; une PR ouverte suffit si review/merge n'étaient pas dans le périmètre. N'écris jamais sur une activité terminale. N'invente pas de tests, tickets, PR ou documents. La publication d'activité ne change aucun état Azure ; une nouvelle User Story Azure exige validation humaine explicite.
