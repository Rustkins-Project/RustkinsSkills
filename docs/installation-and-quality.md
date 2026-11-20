# Installation commune, configuration et qualité

> **Statut :** l'installateur et le socle CLI/UTF-8 sont implémentés ; les huit skills historiques et les deux skills de rédaction documentaire sont présents. Les scénarios de sprint attendent une recette sur une itération réelle.

## Structure du dépôt

```text
RustkinsSkills/
├── install.py
├── shared/
│   └── cli_utf8.py              # helpers installés sous ~/.rustkins-skills/shared/
├── skills/
│   ├── rustkins-activity/          # skill du journal Git
│   │   ├── SKILL.md
│   │   └── references/
│   ├── rustkins-boards/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/
│   ├── rustkins-work/
│   ├── rustkins-ask-team/
│   ├── rustkins-knowledge/
│   ├── rustkins-docs/
│   ├── rustkins-adr/
│   ├── rustkins-sprint-planning/
│   ├── rustkins-sprint-status/
│   └── rustkins-sprint-close/
├── docs/                           # guides, contrats et bilan des jalons
└── tests/
```

Les skills `rustkins-docs`, `rustkins-adr` et les trois skills `rustkins-sprint-*` sont découverts par le même installateur. Les mutations Azure réutilisent le script de `rustkins-boards` et ses gardes de révision ; aucun framework local supplémentaire n'est nécessaire.

## Installation et mises à jour

- L'installateur parcourt les dossiers valides `skills/*/SKILL.md` et copie les **mêmes sources** vers les emplacements Codex et Claude Code, y compris références/scripts.
- Le dossier `shared/` est copié une fois sous `~/.rustkins-skills/shared/` avec la même préparation, sauvegarde et restauration que les skills. Les caches Python générés localement sont ignorés.
- Les prérequis sont déclarés dans `skills/<nom>/requirements.json` par `commands` et, pour Azure, `azure_devops_extension`. Un skill indisponible est ignoré avec diagnostic et code retour non nul ; les autres sont installés.
- Conserver le comportement existant : configuration locale persistante, profil réel, auteur Git, clone de RustkinsActivity, brouillons hors clone, installation sans argument après mise à jour.
- Préserver les modifications locales de configuration, jamais écraser les tokens ; ne pas déplacer les brouillons/journal d'Activity par surprise.
- Préparer toutes les copies dans des dossiers temporaires voisins des destinations, puis remplacer les copies installées. Les anciennes copies modifiées sont conservées dans `<client>/skills/.rustkins-backups/` sur le même volume ; un échec de remplacement restaure les copies précédentes. Les sauvegardes de l'ancienne version sous `~/.rustkins-skills/backups/` restent intactes.
- **Pas de versionnement de skills**, manifest semver, mécanisme de compatibilité ni auto-update en arrière-plan. Procédure : `git pull --ff-only` puis `python install.py` depuis le clone local ; redémarrer le client si nécessaire.
- `install.py --check` vérifie les commandes déclarées, l'extension Azure si demandée, et les chemins/configuration Activity sans installer ni exécuter `setup`. Les connexions et permissions distantes ne sont pas vérifiées à ce stade.

## Configuration locale

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

Les chemins sont propres au poste. L'URL `.invalid` est un exemple fictif, pas une valeur à installer. Une réinstallation conserve les clés déjà configurées sans ajouter de version de schéma. La configuration représente des préférences, pas une autorisation : les commandes vérifient toujours permissions et contexte distant.

### Préflight

- `python` ou `python3`, `git`, `gh`, `az`, extension `azure-devops`, authentification du compte et bon projet ; Rust/Cargo pour le skill Activity existant.
- Ne pas forcer la connexion Azure/GitHub au moment d'installer un skill non concerné ; afficher un état par skill et le remède recommandé.
- La configuration Azure doit pointer sur le bon projet avant tout appel de mutation. Ne jamais supposer qu'un `az devops configure` précédent correspond au projet Rustkins.
- Les appels Discord exigent HTTPS et un token client externe à la configuration JSON. Pour la recette locale uniquement, le client accepte HTTP sur les adresses littérales de boucle locale `127.0.0.1` et `::1` ; aucune autre adresse HTTP n'est autorisée. Le client lit le jeton depuis `RUSTKINS_DISCORD_AI_TOKEN`.
- La validation post-installation vérifie que Codex **et** Claude Code possèdent des copies fonctionnelles et identiques.

## Internationalisation et UTF-8

**Exigence obligatoire**, pas simple préférence :

1. Sources `SKILL.md`, README, scripts, JSON, YAML, HTML et fichiers temporaires en UTF-8 ; convention de préférence **sans BOM**, fins de ligne compatibles.
2. Python : `open(..., encoding="utf-8")`, `json.dumps(..., ensure_ascii=False)` lorsque lisibilité utile, `subprocess.run([...], shell=False, text=True, encoding="utf-8", errors="strict")` pour les sorties réellement UTF-8. Sur Windows, configurer/diagnostiquer le mode UTF-8 du processus (`PYTHONUTF8=1` ou `-X utf8`) en préservant les comportements des commandes qui utilisent un encodage différent.
3. Toujours passer les arguments comme **tableau d'arguments**, jamais concaténer une chaîne PowerShell/Bash contenant des accents, apostrophes ou guillemets. Ne pas journaliser les valeurs sensibles dans un message d'erreur.
4. Passer les corps de PR multiligne par un fichier UTF-8 avec `gh pr create --body-file` **et** `gh pr edit --body-file` ; suivre la vérification ci-dessous après publication. Utiliser aussi des fichiers temporaires pour les appels Azure qui n'exposent pas d'option `--file`.
5. Les champs Azure Description/Acceptance Criteria peuvent être **HTML riches** ; convertir/échapper correctement Markdown ou texte brut si nécessaire, ne pas corrompre le contenu ni le transformer en chaîne JSON.
6. Tester PowerShell Windows, chemins Unicode et espaces, Linux, apostrophe `l'exécution`, guillemets `« … »`, `œ`, `É`, emoji, accents combinés et saut de ligne.
7. Les sorties structurées sont vérifiées par un parseur JSON ; `stderr` est interprété comme diagnostic, pas comme vérité métier.

### Corps de PR multiligne dans PowerShell

Une retouche de la PR #6 a aplati titres et listes Markdown : la sortie texte de `gh pr view --json body --jq .body` capturée dans une variable PowerShell est devenue une collection de lignes, puis sa conversion en chaîne lors de `WriteAllText` les a jointes avec des espaces. Pour **créer ou modifier** une description, conserver le Markdown dans un fichier UTF-8 et passer ce fichier directement à `gh --body-file`. Pour reprendre une description existante, lire l'objet JSON avec `gh pr view --json body | ConvertFrom-Json`, puis accéder à sa propriété `.body` ; ne pas faire l'aller-retour par la sortie texte de `--jq .body`.

Exemple PowerShell pour une modification (remplacer le numéro et le contenu) :

```powershell
$body = @'
## Résumé

- Changement vérifié.
'@
$path = Join-Path $env:TEMP 'rustkins-pr-body.md'
[System.IO.File]::WriteAllText($path, $body, [System.Text.UTF8Encoding]::new($false))
gh pr edit 6 --body-file $path
if ($LASTEXITCODE -ne 0) { throw 'Modification de la PR échouée' }
$published = (gh pr view 6 --json body | ConvertFrom-Json).body
$expected = $body.Replace("`r`n", "`n").TrimEnd([char]10)
$actual = $published.Replace("`r`n", "`n").TrimEnd([char]10)
if ($actual -cne $expected) { throw 'Le Markdown publié diffère du fichier source' }
Remove-Item -LiteralPath $path
```

Conserver le fichier en cas d'échec pour comparer le contenu et réessayer. Cette comparaison détecte notamment la disparition des sauts de ligne ; inspecter aussi le rendu GitHub avant de déclarer la PR prête.

### Helpers disponibles au jalon 2

[`shared/cli_utf8.py`](../shared/cli_utf8.py) fournit `run_cli("az", args)` ou `run_cli("gh", args)`, ainsi que `run_json(...)`, avec `subprocess.run` sans shell, délai de 30 secondes par défaut, sortie strictement UTF-8 et `PYTHONIOENCODING=utf-8` pour les outils Python. Sur Windows, il résout `az.cmd` ou `gh.exe` via `shutil.which` ; pour le lanceur MSI `az.cmd`, il appelle directement le Python embarqué avec `-X utf8 -IBm azure.cli` afin de préserver les arguments et la sortie UTF-8 malgré `-I`, qui ignore les variables `PYTHON*`. Le préflight de l'installateur résout aussi `az.cmd`, avec ses arguments fixes. Aucun retry n'est automatique. Un échec donne une `CliError` qui ne contient ni arguments, ni sortie, ni environnement ; le code retour reste indiqué. Le texte de succès est renvoyé à l'appelant et peut contenir des données sensibles : ne pas le journaliser sans examen.

Les fonctions `read_utf8`, `write_utf8`, `read_json`, `write_json`, `plain_text_to_html` et `temporary_markdown` préservent les accents, sauts de ligne et chemins Unicode. `plain_text_to_html` prend **du texte brut**, échappe les caractères HTML et transforme les sauts de ligne en `<br>` ; elle ne convertit pas du Markdown ou du HTML riche. `temporary_markdown` ferme le fichier avant l'appel CLI, notamment sous Windows, puis le supprime après usage. Les scripts des skills importent ce module depuis `~/.rustkins-skills/shared/` et contrôlent leurs propres mutations.

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
| `gh pr create` puis `gh pr edit` avec contenu français multiligne | Corps publié identique au fichier UTF-8, titres et listes conservés |
| Azure description HTML avec `<`, `&`, `é` | Contenu non tronqué ni double-échappé |
| Commande Azure échoue après effet distant | Relecture, pas de duplication au retry |
| Secrets dans les variables d'environnement | Jamais affichés dans output/Activity/PR |
| Test sur Windows et Linux | Résultat attribué uniquement aux plateformes **réellement** exécutées |
