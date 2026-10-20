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
## Installation des paquets

Les commandes ci-dessous ont été retrouvées dans l’historique du serveur. Les versions installées ont été vérifiées séparément. Les commandes répétées dans l’historique ne sont présentées qu’une fois.

### 1. Services web, SSH et collecte

```bash
sudo apt install -y nginx openssh-server syslog-ng syslog-ng-mod-http
```

Nginx fournit le service HTTP des tests. SSH permet les essais de connexions répétées. Le module HTTP de syslog-ng permet l’envoi des journaux à Elasticsearch.

### 2. Outils nécessaires

```bash
sudo apt install -y curl wget gnupg ca-certificates git nano jq
sudo apt install -y software-properties-common
```

### 3. Suricata

Ajout du dépôt OISF stable et installation :

```bash
sudo add-apt-repository -y ppa:oisf/suricata-stable
sudo apt install -y suricata suricata-update
```

La configuration de l’interface réseau et des règles locales est décrite plus bas.

### 4. Dépôt Elastic 9.x

Téléchargement et conversion de la clé de signature :

```bash
wget -qO /tmp/elastic.asc https://artifacts.elastic.co/GPG-KEY-elasticsearch
sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg /tmp/elastic.asc
```

Ajout du dépôt :

```bash
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/9.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-9.x.list
```

Avant une nouvelle installation, actualiser les listes de paquets avec `sudo apt update`. Cette étape est nécessaire à la reproduction, mais n’apparaît pas dans l’extrait filtré de l’historique.

### 5. Elasticsearch et Kibana

```bash
sudo apt install -y elasticsearch kibana
```

Ces commandes installent les paquets. La reproduction complète nécessite aussi la configuration d’Elasticsearch, de Kibana, des certificats et des autorisations du compte de collecte. Ces étapes restent à détailler.

La configuration de collecte observée est présentée dans le [guide syslog-ng](syslog-ng.md). Aucun mot de passe réel ne doit être ajouté au dépôt.
## Prérequis
Deux VM Ubuntu joignables sur 192.168.56.0/24 sont nécessaires. Le serveur héberge Suricata, Nginx, SSH, syslog-ng, Elasticsearch et Kibana. Ce guide rassemble les commandes d’installation retrouvées dans l’historique, les versions vérifiées et la configuration observée. Les étapes initiales de sécurité Elastic restant à documenter sont précisées à la fin.

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
## Configuration Elasticsearch et Kibana observée

### Elasticsearch

La commande suivante a confirmé une écoute locale sur `127.0.0.1:9200` :

```bash
sudo ss -ltnp 'sport = :9200'
```

Syslog-ng et Kibana se connectent à Elasticsearch en HTTPS sur le serveur.

### Kibana

Les paramètres suivants ont été relevés dans `/etc/kibana/kibana.yml` :

```yaml
server.host: "192.168.56.102"
elasticsearch.hosts: ["https://127.0.0.1:9200"]
elasticsearch.ssl.certificateAuthorities: ["/var/lib/kibana/ca_1792118765468.crt"]
```

Le paramètre `elasticsearch.ssl.certificateAuthorities` désigne un certificat d’autorité présent dans `/var/lib/kibana/`. Ces paramètres ont été relevés dans `/etc/kibana/kibana.yml`.

Kibana écoute sur l’adresse du serveur du laboratoire et se
connecte à Elasticsearch en HTTPS sur l’interface locale.
Le fichier `/var/lib/kibana/ca_1792118765468.crt` est le
certificat d’autorité configuré pour cette connexion.

Sur une nouvelle installation, le nom du certificat peut
différer : utiliser le chemin réellement généré et vérifier
que le service Kibana peut lire ce fichier.

L’interface Kibana du laboratoire est accessible à :
`http://192.168.56.102:5601`

### Vues de données

Dans Discover, les vues utilisées sont :

| Vue | Modèle d’indexation | Champ temporel |
|---|---|---|
| Projet sécurité | projet-* | timestamp |
| Journaux système et web | projet-system-* | timestamp |

Pour créer la vue des journaux système et web :

1. Ouvrir Discover et le sélecteur de vue de données.
2. Choisir « Créer une vue de données ».
3. Saisir le nom « Journaux système et web ».
4. Saisir le modèle `projet-system-*`.
5. Choisir le champ temporel `timestamp`.
6. Enregistrer la vue.

Pour consulter les événements, sélectionner une période couvrant les tests, puis utiliser :

- Alertes Suricata : `event_type : "alert"` dans « Projet sécurité ».
- Journaux SSH : `program : "sshd"` dans « Journaux système et web ».
- Recherche de requêtes GET : `message : *GET*` dans « Journaux système et web ». Examiner le contenu du message pour confirmer qu’il s’agit d’un journal HTTP.

### Limites de reproduction

Cette section décrit les paramètres observés sur le serveur. La procédure initiale de configuration de la sécurité Elastic, de mise en place des certificats et d’attribution des droits au compte de collecte reste à documenter. Les mots de passe et jetons sont exclus du dépôt.
## Sécurité Elasticsearch observée

Les paramètres suivants ont été relevés dans `/etc/elasticsearch/elasticsearch.yml` :

```yaml
xpack.security.enabled: true

xpack.security.http.ssl:
  enabled: true
  keystore.path: certs/http.p12

http.host: 127.0.0.1
```

La sécurité et le chiffrement HTTPS de l’API sont activés. L’API écoute uniquement sur l’adresse locale du serveur.

Le fichier `http.p12` contient du matériel cryptographique privé et reste hors du dépôt. Les clients Kibana et syslog-ng utilisent un certificat d’autorité pour vérifier le certificat du serveur.

Ces paramètres décrivent l’installation observée. Ils ne suffisent pas à recréer les certificats ni les comptes et leurs autorisations.
## Validation des services et des configurations

Vérification effectuée le 20 octobre 2026 à 02:51
(UTC−04:00) sur le serveur Ubuntu.

L’interface du laboratoire `enp0s8` est active et possède
l’adresse `192.168.56.102/24`.

La commande suivante retourne `active` pour les sept services :

    systemctl is-active suricata syslog-ng elasticsearch kibana nginx ssh suricata-notify

La validation de Suricata 8.0.7 a été exécutée avec :

    sudo suricata -T -c /etc/suricata/suricata.yaml

Résultat : configuration chargée avec succès.
Un avertissement concerne la direction de détection de la
règle SSH SID 1000002 ; il n’empêche pas le chargement.

La vérification syslog-ng a également été exécutée :

    sudo syslog-ng --syntax-only

Aucune erreur n’est affichée dans la capture.

Cette vérification confirme l’état des services à cet instant.
Elle ne constitue pas une validation après redémarrage ni,
à elle seule, une preuve de collecte de nouveaux événements.
### Capture de validation
[Validation des services et des configurations](../captures/Validation-services-configurations.jpeg)
