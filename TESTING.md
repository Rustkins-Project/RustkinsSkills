# Validation de la phase 4

Vérifications locales effectuées le 7 novembre 2026 sous Windows :

- `RustkinsActivity`: `cargo fmt --check` et `cargo test --offline` réussis. Le nouveau test `agent_cli.rs` prépare une création Codex, retrouve le brouillon, publie vers un dépôt Git temporaire, découvre la même activité dans une nouvelle session simulée, puis prépare et publie un patch depuis le même clone en conservant l'agent créateur. Il ajoute un second dépôt.
- Les tests existants de RustkinsActivity couvrent création directement `completed`, transitions ouvertes, blocage/reprise, clôture et immutabilité terminale ; publication concurrente, verrou, refus de push, reconstruction et récupération après interruption.
- `RustkinsSkills`: `python -m unittest discover -s tests -v` réussit. Il vérifie l'installation identique pour Codex et Claude Code, le partage de la configuration et la mise à jour sans ressaisie, ainsi que le refus de brouillons placés dans le clone.
- La syntaxe YAML du frontmatter (`name` et `description`) a été relue ; le script `quick_validate.py` fourni par Codex n'a pas pu démarrer dans cet environnement car le module Python `yaml` y est absent.

| Scénario demandé | État |
| --- | --- |
| Première intervention, création | Test CLI + publication Git temporaire |
| Nouvelle session, même intervention | Test CLI de redécouverte du même ID |
| Codex vers Claude Code | Contrat d'installation identique et simulation CLI ; lancement réel Claude Code indisponible |
| Plusieurs activités ouvertes, objectifs distincts | Règle de rapprochement documentée ; décision contextuelle d'agent non testée en session réelle |
| Correspondance ambiguë | Question ciblée prescrite par le skill ; décision contextuelle d'agent non testée en session réelle |
| Intervention multidépôts | Test CLI de patch `add_repository` |
| Correction rapide directement `completed` | Test existant `creates_completed_activity_and_resumes_same_draft` |
| Blocage, reprise, clôture | Tests Rust existants de transitions et clôture ; comportement conversationnel non testé |
| Review après clôture | Immutabilité terminale testée ; création de nouvelle fiche prescrite par le skill, non testée en agent réel |
| Erreur de publication Git et récupération | Tests Rust existants de rejet de push, interruption et reprise |

Le binaire Claude Code n'est pas disponible sur ce poste. Le lancement autonome du skill par Codex et Claude Code n'a donc pas été vérifié en conditions réelles ; les tests utilisent le moteur CLI commun et une simulation de leurs sessions. Après fusion des PR, réaliser un essai contrôlé avec chacun des deux agents et les profils réels, en vérifiant la sélection automatique du skill et la reprise d'une même activité.
