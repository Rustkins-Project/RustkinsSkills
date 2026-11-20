# Contribuer à RustkinsDocs

Pour la rédaction des DOC/RUN, suis le parcours spécialisé [rustkins-docs](../../rustkins-docs/SKILL.md) ; pour les nouvelles ADR, leur acceptation et leur supersession, [rustkins-adr](../../rustkins-adr/SKILL.md). Ce guide conserve le routage et la recherche documentaire transversale ainsi que les connaissances `KNOW`.

Lis `docs/conventions/knowledge-management.md`, `INDEX.md` et le README du dossier cible avant de modifier le dépôt. Le [parcours de lecture](search.md) sert à retrouver les documents voisins et une éventuelle décision antérieure. Une intervention de développement suit aussi [rustkins-activity](../../rustkins-activity/SKILL.md) ; si elle est liée à une Task/US, [rustkins-boards](../../rustkins-boards/SKILL.md) garde le suivi Azure.

## Préparer le changement

Cherche le sujet et ses synonymes dans `docs/`, `decisions/`, `knowledge/` et `research/` avant d'ajouter un fichier. Relis les liens depuis `INDEX.md`, les README et les documents voisins. Si le sujet existe, mets à jour ce document ou propose une correction ciblée ; ne crée pas un doublon pour une autre version du produit sans différence de contrat. Pour un nouveau fichier, vérifie les IDs déjà présents dans tout le dépôt, y compris les références et anciens fichiers : un ID retiré ne se réattribue pas.

Choisis la forme du document :

| Contenu | Dossier et point de départ | Statut prudent |
| --- | --- | --- |
| Décision de conception | `decisions/`, `templates/adr.md`, `schemas/adr.schema.json` | `proposed` ; `decided_at: null`, `approved_by: []` |
| Solution ou observation réutilisable | `knowledge/`, `templates/knowledge.md`, `schemas/knowledge.schema.json` | `candidate` sans preuve ; `verified` avec vérification réelle et `verified_at` |
| Spécification, architecture ou convention | dossier `docs/` approprié, `templates/document.md`, `schemas/document.schema.json` | `draft` jusqu'à validation effective ; tous les `README.md` sont exemptés de frontmatter |
| Procédure opérationnelle | `docs/operations/`, `templates/runbook.md` et `schemas/runbook.schema.json` (`RUN-xxxx`) | Étapes et prérequis vérifiés, sans commande dangereuse implicite |

Renseigne `applies_to` avec la version du **produit Rustkins** (`V0`, `V1`, etc. ou `all` si réellement transversal). `specification_version` désigne un contrat YAML distinct. Préserve les références stables et les preuves ; une réponse validée de Discord est une référence, pas une approbation d'ADR. Si une ADR acceptée est remplacée, prépare une nouvelle ADR `proposed` avec `supersedes`, puis vérifie les liens réciproques utiles sans effacer l'historique. Ne convertis pas automatiquement les rubriques « ADR » historiques de l'architecture en décisions acceptées.

## Branche, vérifications et PR

Vérifie `git status`, la branche et `origin/main`, puis cherche les branches et PR équivalentes avant de créer une contribution. Préserve le clone de lecture : utilise un worktree ou clone d'écriture distinct et une branche explicite issue de la bonne base. Ne pousse pas sur la branche d'un collègue. Pour une modification d'ADR, maintiens `proposed` dans la PR ; l'acceptation exige une revue par **un autre membre humain** et la fusion sur `main`. L'agent ne s'auto-approuve ni ne fusionne.

Avant la PR, vérifie le frontmatter contre le schéma JSON correspondant au YAML parsé si un validateur est disponible ; sinon contrôle les champs obligatoires et signale la limite. Vérifie l'unicité des IDs dans le dépôt, les liens Markdown relatifs, les images, les renvois dans `INDEX.md` et les README, ainsi que les références d'autres dépôts touchées par un déplacement. Exécute les contrôles du dépôt, puis relis le diff pour exclure secrets, transcriptions privées et affirmations sans preuve.

Committe et pousse la branche ; ouvre une PR normale dans RustkinsDocs, avec portée, statut de chaque document, sources, contrôles exécutés et limites. Utilise le fichier UTF-8 et la comparaison du corps distant prescrits par [rustkins-work](../../rustkins-work/references/pr-workflow.md#corps-publication-et-vérification). Pour une ADR, indique explicitement la revue humaine requise. Une note `knowledge/` ne demande pas de revue de pair obligatoire selon la convention, mais la PR reste utile pour sa traçabilité. Après un timeout de push ou de création de PR, relis l'état distant avant de réessayer.
