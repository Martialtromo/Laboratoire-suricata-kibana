# Script de notification

Ajouter ici le fichier notify.py réellement installé et testé sur la VM serveur. Le dossier préparé n'inclut pas une copie supposée de ce fichier : la version réelle peut différer du code proposé dans la conversation.

Depuis un dossier de projet sur la VM, copier uniquement le script :
```bash
sudo cat /opt/suricata-notify/notify.py > scripts/notify.py
```
Inspecter le fichier avant de le publier : il doit lire la configuration externe, sans contenir de mot de passe ni d'adresse personnelle codée en dur.

Ne jamais copier /etc/suricata-notify/smtp.env ni /var/lib/suricata-notify/state.json dans le dépôt. Le test_mail.py n'est pas nécessaire à l'exécution du service.

Pour l'utilisation et les limites, consulter docs/notifications.md.
