# Notifications par courriel

## Configuration
- Gmail expéditeur, avec validation en deux étapes et mot de passe d'application.
- Réception : boîte Outlook scolaire.
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

## Service
Copier configs/suricata-notify.service vers /etc/systemd/system/, après avoir ajouté le véritable script.
```bash
sudo python3 -m py_compile /opt/suricata-notify/notify.py
sudo systemctl daemon-reload
sudo systemctl enable --now suricata-notify
sudo systemctl is-active suricata-notify
sudo journalctl -u suricata-notify -n 20 --no-pager
```
Éviter une seconde instance manuelle pendant que le service tourne.

## Preuves observées
Le message de test SMTP a été reçu. Une alerte SQL a ensuite déclenché un courriel depuis le script manuel. Le service a démarré à 22:55:44 avec Surveillance EVE active. Le journal indique Courriel envoye pour 1000003|192.168.56.101 à 22:57:28 ; réception à 22:57 confirmée. Deux requêtes supplémentaires dans les cinq minutes n'ont pas généré de courriel supplémentaire selon le test rapporté.

L'activation au démarrage est confirmée ; un redémarrage réel de la VM n'a pas encore été testé. Les erreurs SMTP et rotations sont prises en charge dans le code proposé mais n'ont pas été simulées.

Ne jamais publier smtp.env, le code d'application Google, les jetons ou une capture les montrant. Le modèle smtp.env.example ne contient que des valeurs factices.
