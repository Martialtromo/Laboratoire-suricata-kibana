# Supervision réseau avec Suricata et Kibana

Laboratoire réalisé le 19 octobre 2026 sur deux VM Ubuntu sous VirtualBox.

## Objectif
Détecter cinq comportements réseau contrôlés, retrouver les alertes dans Elasticsearch/Kibana et envoyer une notification par courriel avec limitation des doublons.

## Architecture
| Machine | Adresse | Rôle |
|---|---|---|
| Serveur Ubuntu | 192.168.56.102 | Suricata 8.0.7, Nginx, SSH, Elasticsearch, Kibana, notification Python |
| Client Ubuntu | 192.168.56.101 | Nmap, curl et client SSH |

Le trafic du laboratoire passe par `enp0s8`. Sur le serveur, `enp0s3` porte aussi `10.0.2.15` et n'est plus l'interface choisie pour les essais entre VM.

Chaîne : trafic client → Suricata → eve.json → syslog-ng → Elasticsearch → Discover et dashboard Kibana.

Voir la [documentation de la collecte avec syslog-ng](docs/syslog-ng.md).

Le script de notification lit directement eve.json et transmet les messages via Gmail SMTP vers Outlook scolaire.

## Résultats
Les cinq SID 1000001 à 1000005 ont déclenché dans eve.json et ont été retrouvés dans Discover. Le courriel automatique a été reçu ; le service systemd est actif et activé au démarrage. L'anti-doublons a été testé pour le même SID et la même IP source.

Voir [installation](docs/installation.md), [scénarios](docs/scenarios.md), [notifications](docs/notifications.md), [preuves](captures/README.md) et [conclusion](docs/conclusion.md).

## Reproduction
1. Lire les prérequis et adapter les IP, HOME_NET et interfaces.
2. Copier les règles et les déclarer dans suricata.yaml.
3. Valider avec `suricata -T`, puis redémarrer le service.
4. Exécuter les tests uniquement sur les VM du laboratoire.
5. Comparer SID, heure, IP source et destination dans eve.json et Kibana.

## État du dépôt
La documentation, les règles, le script `notify.py` et les captures de preuve sont inclus dans ce dépôt. Le fichier de configuration fourni est un extrait, pas un remplacement complet de suricata.yaml. Les sources et états secrets restent hors du dépôt.

Aucune exploitation réussie n'est revendiquée. Ce laboratoire utilise un IDS passif : il observe et alerte, sans bloquer les requêtes.
