# Installation et configuration observées
## Environnement et versions vérifiés

Le serveur utilise Ubuntu 26.04.1 LTS sous VirtualBox.

| Composant | Version du paquet installé | Dépôt proposant cette version |
|---|---|---|
| Suricata | 1:8.0.7-0ubuntu3 | PPA OISF suricata-stable |
| syslog-ng | 4.8.1-7build2 | Ubuntu universe |
| Elasticsearch | 9.5.5 | Elastic 9.x |
| Kibana | 9.5.5 | Elastic 9.x |

Commandes utilisées pour relever ces informations :

    cat /etc/os-release
    dpkg-query -W suricata syslog-ng elasticsearch kibana
    apt-cache policy suricata syslog-ng elasticsearch kibana

Ces vérifications décrivent l’environnement installé. Elles ne constituent pas un historique des commandes d’installation exécutées.

## Collecte avec syslog-ng

Syslog-ng lit les événements Suricata, les journaux Nginx et les messages d’authentification. Il les transmet à Elasticsearch en HTTPS avec vérification du certificat.

La configuration, les commandes de validation et les preuves de réception dans Kibana sont présentées dans le [guide syslog-ng](syslog-ng.md).

## Prérequis
Deux VM Ubuntu joignables sur 192.168.56.0/24. Sur le serveur, Suricata, Nginx, SSH, Elasticsearch et Kibana étaient déjà présents. Les versions et étapes initiales non relevées ne sont pas inventées ici. Ce guide décrit les modifications réalisées pendant la session, pas un déploiement intégral depuis une VM vierge.

## Vérifications réseau
```bash
ip -br addr
sudo ss -ltnp
sudo systemctl cat suricata
```
Nginx écoute sur le port 80, SSH sur 22, Kibana sur 192.168.56.102:5601. Elasticsearch a été observé en écoute locale.

## Règles
```bash
sudo mkdir -p /etc/suricata/rules
sudo nano /etc/suricata/rules/local.rules
```
Copier le contenu de `configs/local.rules`, une règle par ligne.
Dans `/etc/suricata/suricata.yaml`, conserver les règles existantes et ajouter :
```yaml
rule-files:
  - suricata.rules
  - /etc/suricata/rules/local.rules
```
Dans le bloc `af-packet`, l'interface du laboratoire a été remplacée par `enp0s8`. Ne pas remplacer le YAML complet par l'extrait de ce dépôt. Vérifier que HOME_NET couvre 192.168.56.102 ; sa valeur exacte n'a pas été conservée dans les preuves.

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
sudo systemctl restart suricata
sudo systemctl is-active suricata
```
Résultat observé : configuration chargée avec succès et service actif.

## Outils clients
```bash
sudo apt install nmap curl openssh-client
```
Le premier test TCP de SSH utilise aussi `nc` (paquet netcat-openbsd si absent).

## Kibana
- URL du laboratoire : http://192.168.56.102:5601
- Vue : Projet securite ; modèle : projet-* ; temps : timestamp.
- Filtre KQL : `event_type : "alert"`.
- Colonnes : timestamp, src_ip, dest_ip, alert.signature, alert.severity.
- Recherche enregistrée : Alerte Suricata.
- Dashboard : Supervision Suricata, avec tableau, compteur des enregistrements, chronologie, signatures et IP sources.
- Choisir une période englobant les essais. Les 24 dernières heures ne montreront plus les tests une fois ceux-ci trop anciens ; utiliser une plage absolue pour la remise.

## Validation de la chaîne
L'alerte préexistante SID 2027695 a été retrouvée dans eve.json, dans une réponse Elasticsearch et dans Discover (19:43:54.381, source 10.0.2.15). Index observé : projet-suricata-20261019.
Les cinq règles locales ont ensuite été vérifiées dans eve.json et Discover.
