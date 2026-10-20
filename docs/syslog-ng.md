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
