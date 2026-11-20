# Contrat de travail — rustkins-docs

> **Statut :** nouveau skill de rédaction spécialisée, ajouté à [RustkinsSkills](../../skills/rustkins-docs/SKILL.md). Référence normative : la révision consultée de [RustkinsDocs](https://github.com/Rustkins-Project/RustkinsDocs/blob/main/docs/conventions/knowledge-management.md) ; ce fichier n'est pas une nouvelle gouvernance.

## Quand l'utiliser

« Rédige la spécification du Scheduler V1 », « mets à jour le document de sécurité », « génère un runbook de déploiement », « réorganise l'architecture sans casser les liens ». Traite **DOC** et **RUN** dans `docs/**` ; les ADR vont dans `rustkins-adr` et les connaissances dans `rustkins-knowledge`.

## Contrat

1. Identifier le clone RustkinsDocs, sa branche/révision réelle, les sources applicables et un éventuel document canonique existant.
2. Adapter le texte aux faits réellement fournis, avec versions produit, limites, références et incertitudes ; ne pas inventer de décision ou de résultat de test.
3. Reprendre exactement `templates/document.md` + `schemas/document.schema.json` ou `templates/runbook.md` + `schemas/runbook.schema.json` ; ne pas confondre versions produit et YAML.
4. Conserver les IDs historiques, attribuer un ID neuf et libre pour une création, renseigner `related_docs` en IDs DOC/RUN et `related_adrs` en IDs ADR uniquement. Maintenir les liens et README/INDEX utiles.
5. Vérifier `python scripts/validate_docs.py` ; le contrôle historique contre `main` est garanti en CI PR. Publier une PR dédiée via `git`/`gh` lorsque demandé, sans merge.

## Recette attendue

- Enrichir un DOC existant sans changer son ID, et vérifier sa cohérence de version.
- Créer un RUN dans `docs/operations/` avec les quatre sections H2 non vides ; refuser un exemple invalide.
- Corriger des liens relatifs après déplacement ; ne pas utiliser un chemin dans `related_docs`.
- Publier une PR avec les résultats de validation réellement constatés ; laisser la revue et le merge aux humains.
- Sous Windows, conserver UTF-8 et sauts de ligne du corps de PR.

Détail du parcours : [document-workflow.md](../../skills/rustkins-docs/references/document-workflow.md).
