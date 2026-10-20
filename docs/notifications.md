# Notifications par courriel

## Configuration
- Gmail expéditeur, avec validation en deux étapes et mot de passe d'application.
- Réception : boîte Gmail.
- SMTP : smtp.gmail.com:587 avec STARTTLS.
- Secrets : /etc/suricata-notify/smtp.env, dossier mode 700 et fichier mode 600.
- Script installé : /opt/suricata-notify/notify.py.
- État : /var/lib/suricata-notify/state.json ; ce fichier reste hors du dépôt.

Le script sélectionne event_type=alert et les SID 1000001 à 1000005. Il envoie heure, signature, SID, source, destination, port, sévérité et action suggérée. Les messages sont marqués comme détections de laboratoire, sans affirmer une compromission.

## Fonctionnement prévu dans le script
- Un envoi par couple SID/IP source toutes les 300 secondes.
- Premier démarrage sans état : ignorer les anciennes lignes.
- Sauvegarde de l'offset, du fichier et des envois dans un JSON écrit atomiquement.
- Envois en attente conservés, nouvelle tentative après erreur SMTP.
- Rotation par changement d'inode et troncature gérées pour les cas courants.

Le script n'offre pas une garantie de livraison exactement une fois : un arrêt entre l'acceptation SMTP et la sauvegarde de l'état peut produire un doublon. Une rotation pendant un arrêt prolongé peut laisser des événements d'un ancien fichier non traités. Ces cas ne sont pas testés.

Aucune règle logrotate pour Suricata ou eve.json n’a été
trouvée dans `/etc/logrotate.conf` ou `/etc/logrotate.d/`.
Le bloc EVE de `/etc/suricata/suricata.yaml` utilise
`filename: eve.json` et ne montre pas de paramètre de rotation.

Le script contient une gestion de changements d’inode et
de troncature, mais la rotation EVE n’a pas été testée
sur cette installation. Aucun test de rotation forcée
n’a été effectué afin de ne pas perturber les journaux actifs.
## Installation du service

Les commandes suivantes permettent de reproduire l’installation.
Elles sont à exécuter sur le serveur, depuis la racine du dépôt.

### 1. Installer le script et préparer les répertoires

```bash
sudo install -d -m 755 /opt/suricata-notify
sudo install -d -m 700 /etc/suricata-notify
sudo install -d -m 700 /var/lib/suricata-notify
sudo install -m 644 scripts/notify.py /opt/suricata-notify/notify.py
```

### 2. Configurer les identifiants SMTP

Pour une nouvelle installation uniquement :

```bash
sudo install -m 600 configs/smtp.env.example /etc/suricata-notify/smtp.env
sudo nano /etc/suricata-notify/smtp.env
```

Renseigner les valeurs SMTP localement, sans guillemets autour
des valeurs. Ne pas écraser une configuration déjà fonctionnelle.
Ne jamais publier ce fichier dans GitHub.

### 3. Installer et démarrer le service

```bash
sudo install -m 644 configs/suricata-notify.service /etc/systemd/system/suricata-notify.service
sudo python3 -m py_compile /opt/suricata-notify/notify.py
sudo systemctl daemon-reload
sudo systemctl enable --now suricata-notify
sudo systemctl is-active suricata-notify
sudo journalctl -u suricata-notify -n 20 --no-pager
```

Le service fourni s’exécute avec l’utilisateur root et peut
lire les fichiers protégés. Un compte dédié avec des permissions
limitées constitue une amélioration possible.

### 4. Vérifier une nouvelle notification

Au premier lancement sans état enregistré, le script ignore
les anciennes lignes d’eve.json. Démarrer le service avant
de produire une nouvelle alerte.

Rejouer un scénario du laboratoire, puis vérifier le journal
du service et la réception du courriel. Pour un même SID
et une même IP source, tenir compte du délai de 300 secondes
entre deux notifications.

Éviter de lancer une seconde instance manuelle du script
pendant que le service fonctionne.
## Captures de preuve

- [Voir le courriel d’alerte reçu](../captures/Courriel-alerte.jpeg)
- [Voir l’état du service et le journal d’envoi](../captures/Service-actif.jpeg)
## Preuves observées
Le message de test SMTP a été reçu. Une alerte SQL a ensuite déclenché un courriel depuis le script manuel. Le service a démarré à 22:55:44 avec Surveillance EVE active. Le journal indique Courriel envoye pour 1000003|192.168.56.101 à 22:57:28 ; réception à 22:57 confirmée. Deux requêtes supplémentaires dans les cinq minutes n'ont pas généré de courriel supplémentaire selon le test rapporté.

Le fonctionnement après redémarrage a été vérifié le
20 octobre 2026 : le service était actif et une nouvelle
alerte SID 1000003 à 05:20:38 (UTC−04:00) a donné lieu
à un courriel reçu.

[Voir la validation après redémarrage](installation.md#validation-après-redémarrage-du-20-octobre-2026)

Ne jamais publier smtp.env, le code d'application Google, les jetons ou une capture les montrant. Le modèle smtp.env.example ne contient que des valeurs factices.
### Test de panne SMTP et reprise

Le 20 octobre 2026, une panne SMTP temporaire a été simulée
en configurant un hôte invalide. À 06:25:05, le journal
a affiché « Envoi reporté : gaierror ».

Après restauration de la configuration sauvegardée et
redémarrage du service, l’alerte en attente SID 1000003
a été envoyée à 06:27:48.

[Voir le journal du report et de la reprise](../captures/reprise-notification-smtp.jpeg)
