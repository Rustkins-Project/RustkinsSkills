---
name: rustkins-ask-team
description: Pose une question ciblée à l'équipe Rustkins via RustkinsDiscordBot lorsqu'une décision humaine manque, puis retrouve uniquement la réponse validée, avec reprise idempotente après interruption.
---

# Question à l'équipe Rustkins

Utilise ce skill lorsqu'une décision importante manque dans les sources officielles, qu'une contradiction bloque le travail, ou que l'utilisateur demande explicitement de consulter l'équipe. Lis [le parcours et le contrat du client](references/questions-workflow.md) avant tout appel. Le bot publie une question à des humains : n'envoie la requête que si cette consultation est autorisée dans la demande.

1. Recherche d'abord la réponse dans RustkinsDocs, Azure Boards et les décisions déjà validées pertinentes. Une discussion Discord non validée ne constitue pas une décision. Si la réponse existe, cite sa source et n'ouvre pas de question.
2. Formule une seule question précise, avec le contexte nécessaire et des liens réels. Ne transmets ni secret, ni conversation complète, ni donnée personnelle sans besoin. Prépare un fichier JSON UTF-8 hors dépôt contenant `title`, `question`, `context` et `references`.
3. Lance `prepare --input <fichier>` **avant** tout POST. Cette commande conserve la clé UUID et l'empreinte du contenu dans un état local minimal. En cas d'interruption, reprends avec le même fichier et `submit --input <fichier>` ; ne crée pas une autre question. Garde le fichier d'entrée jusqu'à l'obtention d'un `question_id`.
4. Lance `submit` seulement après les vérifications ci-dessus. Un statut `pending`, y compris si la publication Discord est encore en cours, signifie qu'aucune réponse validée n'est disponible. Communique le `question_id` au développeur et, si une Activity est bloquée, journalise l'action humaine attendue sans recopier le texte sensible.
5. Sur demande ou à la reprise, utilise `get --question-id <UUID>` ou `list` pour retrouver les identifiants locaux. Si `answered`, utilise seulement l'objet `answer` et son URL de provenance. Une réponse durable peut motiver une contribution à RustkinsDocs via [rustkins-knowledge](../rustkins-knowledge/SKILL.md) ; elle n'approuve pas automatiquement une ADR.

Le client ne lance aucun polling en arrière-plan. Un échec réseau ou `429` se reprend manuellement avec `submit` et le même fichier ; un `401`/`403` demande de corriger l'accès, jamais d'emprunter l'identité d'un collègue.
