# Installation commune, configuration et qualité

> **Statut :** le jalon 1 (installateur commun) est implémenté. Les nouveaux skills et leurs intégrations restent au stade de plan.

## Structure de dépôt cible

```text
RustkinsSkills/
├── install.py
├── skills/
│   ├── rustkins-activity/          # existant, à préserver
│   │   ├── SKILL.md
│   │   └── references/
│   ├── rustkins-boards/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/               # seulement si nécessaires
│   ├── rustkins-work/
│   ├── rustkins-ask-team/
│   └── rustkins-knowledge/
├── docs/                           # spécifications et plan
└── tests/
```

Les trois futurs skills `rustkins-sprint-*` seront ajoutés plus tard sous `skills/`. Les contrats partagés peuvent vivre dans un petit module `scripts/` commun **seulement si** plusieurs skills ont un besoin technique identique, avec installation/prérequis documentés ; éviter un framework local générique.

## Installation et mises à jour

- L'installateur parcourt les dossiers valides `skills/*/SKILL.md` et copie les **mêmes sources** vers les emplacements Codex et Claude Code, y compris références/scripts.
- Les prérequis sont déclarés dans `skills/<nom>/requirements.json` par `commands` et, pour Azure, `azure_devops_extension`. Un skill indisponible est ignoré avec diagnostic et code retour non nul ; les autres sont installés.
- Conserver le comportement existant : configuration locale persistante, profil réel, auteur Git, clone de RustkinsActivity, brouillons hors clone, installation sans argument après mise à jour.
- Préserver les modifications locales de configuration, jamais écraser les tokens ; ne pas déplacer les brouillons/journal d'Activity par surprise.
- Préparer toutes les copies dans des dossiers temporaires voisins des destinations, puis remplacer les copies installées. Les anciennes copies modifiées sont conservées dans `<client>/skills/.rustkins-backups/` sur le même volume ; un échec de remplacement restaure les copies précédentes. Les sauvegardes de l'ancienne version sous `~/.rustkins-skills/backups/` restent intactes.
- **Pas de versionnement de skills**, manifest semver, mécanisme de compatibilité ni auto-update en arrière-plan. Procédure : `git pull --ff-only` puis `python install.py` depuis le clone local ; redémarrer le client si nécessaire.
- `install.py --check` vérifie les commandes déclarées, l'extension Azure si demandée, et les chemins/configuration Activity sans installer ni exécuter `setup`. Les connexions et permissions distantes ne sont pas vérifiées à ce stade.

## Configuration locale cible

Exemple **illustratif**, sans secret :

```json
{
  "profile": "Timothy",
  "author": "github-login",
  "activity_clone": "/chemin/local/RustkinsActivity",
  "drafts_dir": "/chemin/persistant/drafts",
  "docs_clone": "/chemin/local/RustkinsDocs",
  "azure": {
    "organization": "https://dev.azure.com/organisation",
    "project": "Rustkins"
  },
  "discord": {
    "base_url": "https://discord-bot.example.invalid"
  }
}
```

Les chemins sont propres au poste. L'URL `.invalid` est un exemple fictif, pas une valeur à installer. Migrer **les clés déjà existantes** sans casser les postes et sans ajout de version de schéma. La configuration représente des préférences, pas une autorisation : les commandes vérifient toujours permissions et contexte distant.

### Préflight

- `python` ou `python3`, `git`, `gh`, `az`, extension `azure-devops`, authentification du compte et bon projet ; Rust/Cargo pour le skill Activity existant.
- Ne pas forcer la connexion Azure/GitHub au moment d'installer un skill non concerné ; afficher un état par skill et le remède recommandé.
- La configuration Azure doit pointer sur le bon projet avant tout appel de mutation. Ne jamais supposer qu'un `az devops configure` précédent correspond au projet Rustkins.
- Les appels HTTP Discord exigent HTTPS, URL de base autorisée et token client externe à la configuration JSON. Prévoir lecture sûre depuis variable d'environnement ou coffre OS.
- La validation post-installation vérifie que Codex **et** Claude Code possèdent des copies fonctionnelles et identiques.

## Internationalisation et UTF-8

**Exigence obligatoire**, pas simple préférence :

1. Sources `SKILL.md`, README, scripts, JSON, YAML, HTML et fichiers temporaires en UTF-8 ; convention de préférence **sans BOM**, fins de ligne compatibles.
2. Python : `open(..., encoding="utf-8")`, `json.dumps(..., ensure_ascii=False)` lorsque lisibilité utile, `subprocess.run([...], shell=False, text=True, encoding="utf-8", errors="strict")` pour les sorties réellement UTF-8. Sur Windows, configurer/diagnostiquer le mode UTF-8 du processus (`PYTHONUTF8=1` ou `-X utf8`) en préservant les comportements des commandes qui utilisent un encodage différent.
3. Toujours passer les arguments comme **tableau d'arguments**, jamais concaténer une chaîne PowerShell/Bash contenant des accents, apostrophes ou guillemets. Ne pas journaliser les valeurs sensibles dans un message d'erreur.
4. Préférer les fichiers UTF-8 pour les messages longs ou multilignes : `gh pr create --body-file`, fichiers temporaires au besoin pour les appels Azure qui n'exposent pas d'option `--file`.
5. Les champs Azure Description/Acceptance Criteria peuvent être **HTML riches** ; convertir/échapper correctement Markdown ou texte brut si nécessaire, ne pas corrompre le contenu ni le transformer en chaîne JSON.
6. Tester PowerShell Windows, chemins Unicode et espaces, Linux, apostrophe `l'exécution`, guillemets `« … »`, `œ`, `É`, emoji, accents combinés et saut de ligne.
7. Les sorties structurées sont vérifiées par un parseur JSON ; `stderr` est interprété comme diagnostic, pas comme vérité métier.

## Pratiques d'intégration

- Les commandes non purement locales ont timeout et code retour contrôlé ; vérifier l'objet distant après la mutation.
- Les scripts doivent être **sans effets secondaires en lecture**. Les opérations d'écriture nécessitent un ID de référence connu et les contrôles de gouvernance.
- Pas de nouvelles dépendances Python non indispensables ; si ajout d'une bibliothèque, documenter son installation et une version de bibliothèque testée (cela **n'est pas** un versionnement des skills).
- Dans les tests, mocker `az`, `gh`, le client HTTP et les erreurs (y compris perte de réponse après succès distant). Ne pas toucher au véritable backlog par défaut.
- Ne pas publier des logs contenant PAT, bearer ou secrets ; messages d'erreur contextualisés sans fuite.
- Vérifier les liens, Markdown, sections de SKILL.md et leur activation effective dans les deux agents. Les instructions doivent expliquer quand utiliser le skill, pas seulement énumérer des commandes.

## Matrice de recette minimale

| Cas | Attendu |
| --- | --- |
| Installation initiale puis relance sans argument | Identité et chemins conservés ; deux clients installés |
| Un skill avec outil manquant | Diagnostic spécifique, autres skills disponibles |
| Échec au milieu d'une copie | Installation précédente préservée ou récupération propre |
| `az` retourne JSON accentué | Parsing correct et accents intacts |
| `gh pr create` avec contenu français multiligne | Corps identique au fichier UTF-8 |
| Azure description HTML avec `<`, `&`, `é` | Contenu non tronqué ni double-échappé |
| Commande Azure échoue après effet distant | Relecture, pas de duplication au retry |
| Secrets dans les variables d'environnement | Jamais affichés dans output/Activity/PR |
| Test sur Windows et Linux | Résultat attribué uniquement aux plateformes **réellement** exécutées |
