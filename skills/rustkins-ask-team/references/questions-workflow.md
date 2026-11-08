# Client des questions RustkinsDiscordBot

Le script [`questions.py`](../scripts/questions.py) utilise uniquement la bibliothèque standard Python. Il suit le contrat déjà exposé par `POST /internal/questions` (202) et `GET /internal/questions/{questionId}` (200). Le bot déduit l'auteur du jeton client IA et publie le thread Discord de manière asynchrone.

## Configuration

Configurer `discord.base_url` avec une URL HTTPS via l'installateur `--discord-base-url` ou dans `~/.rustkins-skills/config.json`. Placer le jeton du développeur dans la variable d'environnement `RUSTKINS_DISCORD_AI_TOKEN`, jamais dans le dépôt, le JSON de configuration, la question ou une Activity. Le client refuse les redirections HTTP pour éviter de transmettre le jeton à une autre origine et fixe un délai de 15 secondes par requête.

Créer un fichier JSON UTF-8 **hors dépôt** avec les champs réels suivants :

```json
{
  "title": "Décision sur le traitement d'un échec",
  "question": "Quelle option l'équipe valide-t-elle ?",
  "context": "Décisions existantes consultées ; options et conséquence de chacune.",
  "references": [
    {"label": "PR", "url": "https://github.com/Rustkins-Project/exemple/pull/4"}
  ]
}
```

Les liens ci-dessus sont illustratifs : remplace-les par des liens HTTPS existants ou utilise `[]`. N'ajoute pas `idempotency_key` au fichier ; le client la crée et l'enregistre une fois.

## Préparer, envoyer, reprendre

Depuis le dossier du skill installé ou du dépôt :

```text
python scripts/questions.py prepare --input <fichier.json>
python scripts/questions.py submit --input <même-fichier.json>
python scripts/questions.py list
python scripts/questions.py get --question-id <UUID>
```

`prepare` calcule une empreinte SHA-256 du JSON normalisé et crée `~/.rustkins-skills/ask-team/<profil>/questions/<empreinte>.json` avec la clé d'idempotence, la date et, après réponse au POST, le `question_id`. Elle ne garde ni texte ni jeton ; le profil humain configuré sépare les états des développeurs. Deux `prepare` avec le même contenu et le même profil retournent la même clé ; deux envois avec cette clé désignent la même question côté bot. Ne modifie pas le contenu entre `prepare` et `submit`. Si le POST a abouti mais que son accusé est perdu, relancer `submit` avec le même fichier réutilise la clé. Dès qu'un `question_id` est enregistré, `submit` consulte GET au lieu de refaire POST.

La sortie de `list` fournit les identifiants et empreintes sans contenu. Garde le fichier d'entrée tant que le `question_id` est inconnu. Une fois l'ID obtenu, conserve l'état local pour retrouver la question à la session suivante. La conservation est manuelle : après réponse validée et si aucune reprise n'est nécessaire, le développeur peut supprimer le fichier `<empreinte>.json` correspondant. Cette suppression permettrait de préparer à nouveau le même texte avec une nouvelle clé ; elle ne supprime rien du bot.

`pending` n'est pas une réponse. `publication_status` et `discord_thread_url` peuvent évoluer après le POST. Seul `answer` lorsque `status` vaut `answered` contient le texte validé, son URL de message et l'identité de validation. Le client n'attend pas la réponse en arrière-plan et ne traite pas les messages libres du thread.

## Erreurs et limites

Les erreurs HTTP 400/401/403/404/409/429/5xx et réseau produisent un diagnostic sans corps de réponse ni jeton. Après timeout, `429` ou `5xx`, reprendre avec le même fichier ; après `409`, vérifier que son contenu correspond à la préparation. Les réponses inattendues ou non UTF-8 sont refusées. Un GET `404` peut signifier une question absente ou non accessible avec cette identité ; ne réessaie pas avec le jeton d'autrui.

Les tests du dépôt simulent POST/GET et ne publient aucune question sur Discord. Une recette réelle nécessite un bot configuré, un jeton propre au développeur et une validation humaine ; elle n'est pas déduite des tests simulés.
