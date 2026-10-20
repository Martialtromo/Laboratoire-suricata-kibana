# Collecte des journaux avec syslog-ng

## Rôle
Syslog-ng collecte les journaux de sécurité du serveur et les transmet à Elasticsearch. Kibana permet ensuite de les consulter.

## Configuration utilisée
Le fichier installé sur le serveur est :
`/etc/syslog-ng/conf.d/projet.conf`

Une copie sans mots de passe est disponible dans :
[syslog-ng-projet.conf.example](../configs/syslog-ng-projet.conf.example)

## Journaux collectés
- Suricata : `/var/log/suricata/eve.json`, pour les alertes des cinq scénarios et les autres événements réseau.
- Nginx : `/var/log/nginx/access.log` et `/var/log/nginx/error.log`, pour examiner les requêtes HTTP et les erreurs.
- Authentification : messages des catégories `auth` et `authpriv`, pour examiner notamment les connexions SSH.

Ces sources permettent de comparer une détection réseau avec les événements du service concerné. Un scan TCP peut produire une alerte Suricata sans événement d’authentification ou requête HTTP.

## Transmission à Elasticsearch
Syslog-ng envoie les événements à `https://localhost:9200/_bulk` avec authentification et vérification du certificat TLS.

Les événements Suricata sont dirigés vers les index `projet-suricata-*`. Les journaux web et d’authentification sont dirigés vers `projet-system-*`.

## Vérifications
Vérifier que le service fonctionne :

    systemctl is-active syslog-ng

Vérifier la syntaxe de la configuration :

    sudo syslog-ng --syntax-only

Consulter les messages du service :

    sudo journalctl -u syslog-ng -n 30 --no-pager

Le service syslog-ng est actif et la vérification de syntaxe a retourné le code 0. Les alertes Suricata et les journaux SSH sont visibles dans Kibana. Un journal web affiche également la requête GET /?test=UNION%20SELECT provenant de 192.168.56.101, avec une réponse HTTP 200. Cette réponse ne prouve pas une injection SQL réussie.

### Preuves
- [Validation de la configuration](../captures/syslog-ng%20validation.jpeg)
- [Journaux SSH dans Kibana](../captures/journaux-ssh-kibana.jpeg)
- [Requête web dans Kibana](../captures/journaux-web-kibana.jpeg)
## Sécurité
Les mots de passe sont remplacés dans l’exemple publié. Cet exemple doit être adapté localement avant utilisation ; il ne remplace pas directement la configuration du serveur.
## Vérification de la collecte après changement du mot de passe

Un événement de test a été généré sur le serveur :

```bash
logger -p auth.notice -t verification-collecte "Test de collecte apres mise a jour"
```

Dans Discover, la vue « Journaux système et web » a été sélectionnée avec une période couvrant le test et le filtre :

```text
program : "verification-collecte"
```

Le message a été retrouvé dans Kibana, confirmant la réception de ce nouvel événement après le changement du mot de passe du compte de collecte.

[Voir la preuve de réception](../captures/verification-collecte.jpeg)
## Mise en place de la collecte sur une nouvelle installation

Cette procédure complète la configuration fournie dans le dépôt.
Elle ne doit pas écraser une installation déjà fonctionnelle.

### 1. Installer le certificat d’autorité

Depuis le serveur Elasticsearch, copier son certificat
d’autorité public vers le répertoire utilisé par syslog-ng :

```bash
sudo install -d -m 755 /etc/syslog-ng/certs
sudo install -m 644 -o root -g root \
  /etc/elasticsearch/certs/http_ca.crt \
  /etc/syslog-ng/certs/http_ca.crt
```

Adapter le chemin source si le certificat Elasticsearch
se trouve ailleurs. Copier uniquement le certificat public,
pas une clé privée ni le fichier http.p12.

Sur le serveur du laboratoire, le certificat de destination
a été vérifié avec :

```bash
sudo ls -l /etc/syslog-ng/certs/http_ca.crt
```

Résultat observé : propriétaire root:root et permissions 644.

### 2. Installer la configuration

Depuis la racine du dépôt, sur une nouvelle installation :

```bash
sudo install -m 600 -o root -g root \
  configs/syslog-ng-projet.conf.example \
  /etc/syslog-ng/conf.d/projet.conf
sudo nano /etc/syslog-ng/conf.d/projet.conf
```

Remplacer les deux valeurs `REMPLACER_LOCALEMENT` par le
mot de passe du compte `projet_ingest`.

Vérifier que la source `s_src` existe dans la configuration
principale. Adapter sa référence si elle porte un autre nom.

Le processus syslog-ng doit pouvoir lire la configuration,
le certificat et les journaux Suricata et Nginx.
Adapter les permissions si le service utilise un compte dédié.

### 3. Valider et démarrer

```bash
sudo syslog-ng --syntax-only
sudo systemctl enable --now syslog-ng
sudo systemctl restart syslog-ng
sudo journalctl -u syslog-ng -n 30 --no-pager
```

### 4. Vérifier la réception

```bash
logger -p auth.notice -t verification-collecte "Test de collecte"
```

Dans Discover, sélectionner la vue des journaux système
et web, une période couvrant le test, puis rechercher :

```text
program : "verification-collecte"
```

Vérifier la présence du nouveau message : un service actif
ne suffit pas à confirmer la réception dans Elasticsearch.
