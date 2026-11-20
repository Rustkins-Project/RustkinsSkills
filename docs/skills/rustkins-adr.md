# Contrat de travail — rustkins-adr

> **Statut :** nouveau skill pour les propositions de décision ; [instructions opérationnelles](../../skills/rustkins-adr/SKILL.md). Référence normative : [RustkinsDocs](https://github.com/Rustkins-Project/RustkinsDocs/blob/main/docs/conventions/knowledge-management.md) et son schéma ADR.

## Quand l'utiliser

« Propose une ADR sur le moteur de cache », « compare et consigne les alternatives », « formalise l'arbitrage validé par l'équipe », « remplace une ancienne ADR ». Ne pas l'utiliser pour un simple document d'architecture : employer `rustkins-docs`. Les recherches de précédents sont faites avec `rustkins-knowledge`.

## Contrat

1. Identifier le sujet, les alternatives réelles, les ADR précédentes et les versions concernées ; ne pas inférer une décision d'une discussion ou d'un document historique.
2. Utiliser le template/schéma ADR courant dans `decisions/**`, avec un nouvel ID unique `ADR-xxxx`, `status: proposed`, `decided_at: null`, `approved_by: []`.
3. Rédiger les quatre H2 imposés `Contexte`, `Décision`, `Alternatives`, `Conséquences`, en distinguant faits, comparaison et points à trancher.
4. Un remplacement `supersedes` annoncé dans une `proposed` **ne rend pas** l'ancienne ADR `superseded`. La promotion après décision humaine doit rendre cohérents les statuts de toutes les ADR affectées dans la même PR.
5. Vérifier le dépôt avec `python scripts/validate_docs.py`, puis préparer une PR. Une approbation humaine de `rustkins-team` est obligatoire pour `decisions/**` ; l'agent ne peut ni approuver ni fusionner.

## Recette attendue

- Créer une ADR de décision encore ouverte : proposition complète mais **pas** d'acceptation inventée.
- Détecter une cible `supersedes` inexistante, auto-référence ou cycle.
- Démontrer qu'une ADR `proposed` avec `supersedes` peut rester valide avec l'ancien statut `accepted`.
- Pour un remplacement réellement accepté, produire une PR cohérente : nouvelle `accepted` et anciennes `superseded`, sans supprimer les fichiers.
- Vérifier le statut du check GitHub et de l'approbation humaine sans déclarer un succès avant leur constat.

Détail du parcours : [adr-workflow.md](../../skills/rustkins-adr/references/adr-workflow.md).
