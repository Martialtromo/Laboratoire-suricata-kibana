# Script de notification Suricata

Le script `notify.py` est inclus dans ce dossier.

Il surveille `/var/log/suricata/eve.json` et sélectionne les
alertes correspondant aux SID 1000001 à 1000005.

Il envoie un courriel contenant l’heure, la signature,
les adresses IP, le port de destination, la sévérité et
une action suggérée.

Les notifications sont limitées à un envoi par couple
SID/IP source toutes les 300 secondes.

## Fichiers utilisés sur le serveur

- Script : `/opt/suricata-notify/notify.py`
- Configuration SMTP : `/etc/suricata-notify/smtp.env`
- État persistant : `/var/lib/suricata-notify/state.json`
- Service : `suricata-notify.service`

Les identifiants SMTP et le fichier d’état restent hors du dépôt.

## Documentation

- [Fonctionnement, validation et limites](../docs/notifications.md)
- [Modèle de configuration SMTP](../configs/smtp.env.example)
- [Service systemd](../configs/suricata-notify.service)
