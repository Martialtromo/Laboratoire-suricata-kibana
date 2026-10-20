# Mettre ce dossier sur GitHub sans connaître Git

1. Décompresser l'archive sur votre ordinateur.
2. Compléter scripts/notify.py depuis la VM et ajouter les preuves dans captures/.
3. Se connecter à https://github.com avec son compte.
4. Cliquer sur + puis New repository (Nouveau dépôt).
5. Nom conseillé : laboratoire-suricata-kibana.
6. Choisir Private pour préparer le travail. Ne pas initialiser un README supplémentaire : celui-ci existe déjà.
7. Cliquer sur Create repository.
8. Sur la page du dépôt vide, choisir uploading an existing file.
9. Glisser le CONTENU du dossier projet-suricata (README.md, docs/, configs/, scripts/, captures/, .gitignore), pas le ZIP et pas le dossier parent.
10. Vérifier que README.md est bien à la racine. La page Web peut ignorer un fichier caché comme .gitignore ; le créer au besoin avec Add file > Create new file.
11. Vérifier qu'aucun smtp.env ni secret n'est présent : .gitignore ne protège pas un secret téléversé volontairement via le navigateur.
12. Message de commit : Documentation du laboratoire Suricata et des tests. Cliquer sur Commit changes.
13. Ouvrir le README et suivre les liens pour vérifier la structure.

Si la remise exige un dépôt public, ne changer la visibilité qu'après relecture des fichiers et captures. Un secret publié doit être révoqué chez le fournisseur : le supprimer d'une page ne l'efface pas de l'historique.

Le PDF précédent peut être ajouté dans rapports/ ; il décrit l'état avant la mise en place des notifications. La documentation Markdown de cette archive inclut les notifications réalisées ensuite.
