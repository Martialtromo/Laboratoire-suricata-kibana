# Conclusion et limites

Les cinq scénarios ont déclenché les SID attendus et leurs alertes ont été retrouvées dans eve.json et Discover. Le dashboard offre une synthèse des alertes. La notification Gmail vers Outlook a été reçue et le service systemd est actif. Le test rapporté confirme la suppression des doublons pendant cinq minutes pour le même SID et la même source.

## Limites
- Faux positifs possibles ; la règle TCP mesure une fréquence de SYN, pas la diversité des ports.
- Recoupement entre rafale HTTP et règle TCP ; les totaux ne sont pas des attaques distinctes.
- Une tentative détectée ne démontre pas une exploitation réussie.
- Le contenu HTTPS chiffré n'est pas inspecté par ces règles HTTP sans mécanisme adapté.
- Les services sont réunis sur une VM, avec un point de défaillance unique.
- L'IDS passif ne bloque pas les attaques.
- Les règles à motifs simples ne couvrent pas toutes les variantes et encodages.
- Le compte SSH de test était inexistant ; aucune force brute de mots de passe démontrée.
- L'acheminement SMTP accepté ne garantit pas à lui seul la réception : celle-ci a été confirmée séparément.

## À compléter avant remise
- [x] Cinq scénarios, règles et SID identifiés.
- [x] Alertes retrouvées dans eve.json et Kibana.
- [x] Dashboard créé avec cinq panneaux.
- [x] Courriel automatique reçu et anti-doublons testé.
- [x] Script notify.py installé sur la VM copié dans scripts/.
- [x] Captures des cinq scénarios et preuves de collecte ajoutées, avec explications dans la documentation.
- [x] Contrôle négatif documenté : réponse HTTP 200 horodatée et recherche Kibana sans alerte correspondante, avec liens vers les deux captures dans docs/scenarios.md.
- [ ] Vérifier les services après un redémarrage réel de la VM.
- [ ] Tester les erreurs d'envoi et la rotation EVE pour étendre la validation.
- [ ] Relire tous les fichiers et vérifier l'absence de secrets avant publication.

Améliorations possibles : compte de service dédié pour les notifications, meilleure journalisation des doublons, suivi des anciens fichiers tournés pendant les arrêts, ajustement des seuils et séparation des services.
## Perspectives et veille technologique

La veille portera sur les avis de sécurité et les notes de version de Suricata, syslog-ng, Elasticsearch et Kibana.

Les mises à jour seront d’abord évaluées sur une copie du laboratoire. Les cinq scénarios seront rejoués pour vérifier la détection, la collecte, la visualisation et les notifications.

Les améliorations envisagées sont l’ajustement des seuils pour réduire les faux positifs, la surveillance des interruptions de collecte et une politique de conservation des journaux adaptée à l’espace disponible.
