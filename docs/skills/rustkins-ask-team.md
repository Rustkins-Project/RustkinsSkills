# Spécification — rustkins-ask-team

> **Statut :** implémenté au jalon 5 dans [`skills/rustkins-ask-team/`](../../skills/rustkins-ask-team/SKILL.md). Les tests du client simulent le bot ; la recette réelle avec validation humaine reste à conduire. **Bot existant** : aucune modification de son API requise.
> Contrat de référence : [RustkinsDiscordBot D2](https://github.com/Rustkins-Project/RustkinsDiscordBot/blob/main/docs/01-cahier-des-charges.md).

## Usage

Demander une décision humaine quand un choix important n'est pas documenté ou qu'une dépendance bloque l'agent, **sans** interpréter une conversation Discord non validée comme une décision. Le skill peut être invoqué seul ou depuis `rustkins-work`, `rustkins-boards` ou `rustkins-knowledge`.

Déclencheurs : une ADR nouvelle, une contradiction entre sources officielles, un choix de périmètre/architecture non autorisé, une dépendance entre développeurs ou une instruction « demande à l'équipe ».

## Contrat API actuel

- `POST /internal/questions` — HTTP `202 Accepted`, authentification bearer **token de client IA du développeur**, clé `idempotency_key` UUID durable ; le bot connaît l'auteur depuis ce token.
- `GET /internal/questions/{questionId}` — HTTP `200` avec `question_id`, `status`, `publication_status`, `discord_thread_url`, `answer` optionnelle.
- États métier : `pending` / `answered`. La publication Discord est asynchrone et peut ne pas être prête lors de la réponse du POST.
- Exemple de **requête** (les champs sont définis par les records C# existants) :

```json
{
  "idempotency_key": "7735c4c1-2c35-4ced-aae7-ec124ac62904",
  "title": "Décision sur l'exécution distribuée",
  "question": "Valide-t-on la séparation du module de scheduling ?",
  "context": "US AB#142 ; décisions existantes consultées ; deux options identifiées.",
  "references": [
    {"label": "US", "url": "https://dev.azure.com/organisation/projet/_workitems/edit/142"}
  ]
}
```

L'URL est **illustrative** : générer les véritables liens depuis la configuration, ne pas inventer des liens lors d'un appel réel.

## Workflow fiable

1. Rechercher dans RustkinsDocs et Azure les décisions déjà validées. Si la réponse est explicite et actuelle, ne pas créer une question parasite.
2. Formuler une question précise, contextualisée et bornée ; joindre seulement des URLs utiles. Ne pas transmettre l'intégralité d'une session IA ou des secrets.
3. Produire un UUID d'idempotence **une seule fois** et le conserver dans un état local non secret, lié à la question (et éventuellement à l'Activity). En cas de timeout POST, **réutiliser le même UUID** plutôt que créer un doublon.
4. Appeler POST ; contrôler la réponse, consigner `question_id` et l'URL de thread si disponible ; l'agent peut passer l'Activity en `blocked` avec l'action attendue.
5. Si `pending`, retourner au développeur une synthèse et l'ID ; **ne pas prétendre attendre ou relancer une conversation de manière autonome en arrière-plan**.
6. Sur reprise de session ou commande explicite, interroger GET avec le `question_id` déjà connu. Si `answered`, utiliser uniquement l'objet `answer` validé et sa provenance ; si `pending`, le signaler.
7. Lorsque la réponse conduit à une décision durable, `rustkins-knowledge` prépare si nécessaire l'ADR/PR ; Discord ne publie ni n'approuve automatiquement une ADR.

## Client local et sécurité

Un script Python HTTP ciblé est justifié ici : pas de `gh`/`az` pour interagir avec les questions du bot. Le script gère JSON UTF-8, TLS, bearer, timeout, HTTP 400/401/403/404/409/429/5xx, retries prudents et idempotence.

- URL de base dans la configuration locale ; token dans variable d'environnement ou coffre local hors dépôt. Ne jamais écrire le token dans `~/.rustkins-skills/config.json`, un dump d'erreur, une Activity, une PR ou Discord.
- Les clés d'idempotence et IDs de question, **pas le texte sensible**, sont conservés dans un état local minimal à la reprise. La conservation est manuelle : supprimer le fichier de l'empreinte seulement après réponse validée et lorsque la reprise n'est plus nécessaire.
- GET peut signaler un refus pour un autre auteur : ne pas réessayer avec l'identité d'un coéquipier.
- Les sorties textuelles doivent préserver tous les accents, guillemets français, liens et caractères Unicode.
- Le script n'a aucune intégration Azure dans le bot : les références Azure sont fournies par l'agent au moment de la requête.

## Recette

POST dupliqué avec même UUID → même question ; POST interrompu puis repris → pas deux threads ; GET `pending` → pas de réponse inventée ; validation humaine dans Discord → GET `answered` exploitable, source citée ; token erroné → refus explicite ; échec Discord → état durable et reprise ; texte français préservé.
