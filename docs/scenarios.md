# Scénarios et résultats

Tests envoyés depuis 192.168.56.101 vers 192.168.56.102, le 19 octobre 2026, heure locale UTC-04:00.

| Scénario | SID | Heure | Résultat Discover observé |
|---|---|---|---|
| SYN TCP fréquents | 1000001 | 21:26:10 | 80 alertes au premier essai |
| Connexions SSH répétées | 1000002 | 21:33:27 puis 22:14:17 | 3 alertes par essai observé |
| Motif SQL HTTP | 1000003 | 21:07:18.343 | 1 alerte |
| Parcours de chemin | 1000004 | 21:44:23.272 | 1 alerte |
| GET fréquents | 1000005 | 21:50:24 | 10 alertes |

## 1. Scan TCP
```bash
sudo nmap -sS -Pn -p 1-100 --max-retries 0 --min-rate 50 192.168.56.102
```
Seuil : plus de 20 SYN en 10 secondes par source. L'option min-rate a été ajoutée pour atteindre ce seuil. La règle compte les SYN, sans imposer des ports distincts : une activité légitime intense peut aussi déclencher.

## 2. SSH répété
Premier contrôle TCP :
```bash
for i in {1..8}; do nc -z -w 1 192.168.56.102 22; done
```
Puis contrôle avec le client SSH :
```bash
for i in {1..8}; do
  ssh -o BatchMode=yes -o ConnectTimeout=2 \
    -o StrictHostKeyChecking=accept-new \
    -o PubkeyAuthentication=no utilisateur_test@192.168.56.102 true
done
```
Seuil : plus de 5 SYN vers 22 en 60 secondes. Le compte utilisateur_test était inexistant. Le journal signale Invalid user et Connection closed [preauth], sans essai de mot de passe. Les ports sources 57804, 57812 et 57828 concordent avec les alertes à 22:14:17.
```bash
sudo journalctl -u ssh --since "2026-10-19 22:13:00" --until "2026-10-19 22:16:00" --no-pager
```

## 3. SQL
```bash
curl --max-time 10 "http://192.168.56.102/?test=UNION%20SELECT"
```
Détection de UNION suivi de SELECT dans l'URI. Réponse Nginx reçue. Aucune base vulnérable ni injection réussie démontrée.

## 4. Parcours de chemin
```bash
curl --path-as-is --max-time 10 "http://192.168.56.102/../test-lab"
```
Détection de ../ dans http.uri.raw. Nginx a répondu 400 ; aucun accès à un fichier démontré.

## 5. Fréquence HTTP
```bash
for i in {1..30}; do
  curl -s --max-time 2 -o /dev/null "http://192.168.56.102/?test=frequence"
done
```
Seuil : plus de 20 GET en 10 secondes par source. Rafale bornée à 30 ; pas de déni de service démontré. Cette rafale peut aussi déclencher la règle TCP.

## Vérification commune
Sur le serveur (adapter le SID) :
```bash
sudo grep '"signature_id":1000003' /var/log/suricata/eve.json | tail -n 3
```
Dans Discover :
```text
event_type : "alert" and alert.signature_id : 1000003
```
Comparer l'heure, le SID, l'IP source et la destination. Les comptes sont des alertes, pas un nombre d'attaques distinctes.

## Contrôle négatif
Après au moins 60 secondes sans test :
```bash
date -Is
curl --max-time 10 -o /dev/null -s -w 'HTTP %{http_code}\n' http://192.168.56.102/
```
Dans Discover, sur une période englobant cette requête et excluant les anciens essais :
```text
event_type : "alert" and alert.signature_id >= 1000001 and alert.signature_id <= 1000005
```
### Résultat du contrôle négatif du 20 octobre 2026

La requête HTTP normale envoyée vers http://192.168.56.102/
entre 03:13:18 et 03:13:19 (America/Toronto, UTC−04:00)
a reçu une réponse HTTP 200.

Dans Discover, sur la période du 20 octobre 2026 de 03:13
à 03:14, aucun résultat n’a été retrouvé avec le filtre
des SID 1000001 à 1000005 présenté ci-dessus.

Ce résultat est cohérent avec le comportement attendu
pour cette requête normale. Il ne garantit pas l’absence
de faux positifs pour tous les trafics légitimes.

- [Voir la preuve terminal HTTP 200](../captures/controle-negatif-terminal.jpeg)
- [Voir la vérification Kibana](../captures/controle-negatif-kibana.jpeg)
## Justification des scénarios et journaux prioritaires

### 1. Scan TCP — SID 1000001
Ce scénario représente une recherche de services accessibles, étape possible de reconnaissance avant une attaque.

Les alertes Suricata permettent d’examiner l’heure, l’IP source, la destination et les ports ciblés. La règle compte des SYN fréquents : elle ne prouve pas à elle seule un scan de ports distincts.

Action suggérée : identifier la source et vérifier si cette activité est autorisée.

### 2. Connexions SSH répétées — SID 1000002
Ce scénario permet de détecter une fréquence inhabituelle de connexions au service d’administration.

Comparer les alertes Suricata aux journaux SSH dans Kibana avec `program : "sshd"`. Vérifier les heures, les IP et les ports sources lorsqu’ils sont disponibles.

Le test réalisé montre des connexions avec un utilisateur inexistant, sans essai de mot de passe. Il ne démontre donc pas une attaque par force brute sur les mots de passe.

Action suggérée : examiner les comptes visés et rechercher d’éventuelles authentifications réussies.

### 3. Motif SQL dans une URL — SID 1000003
Le motif UNION SELECT représente une recherche possible de vulnérabilité d’injection SQL.

Comparer l’alerte Suricata au journal d’accès Nginx : heure, IP source, URL et code de réponse HTTP.

La réponse HTTP 200 observée indique que le serveur a répondu ; elle ne démontre pas une injection SQL réussie.

Action suggérée : examiner l’application et ses journaux avant de conclure à une exploitation.

### 4. Parcours de chemin — SID 1000004
Le motif ../ représente une tentative possible de remonter dans les répertoires pour atteindre une ressource non autorisée.

Comparer l’alerte Suricata aux journaux d’accès et, si disponibles, d’erreur Nginx.

Le serveur a répondu HTTP 400 pendant le test. Aucun accès à un fichier sensible n’a été démontré.

Action suggérée : vérifier le chemin demandé et le traitement des URL par le serveur et l’application.

### 5. Requêtes HTTP fréquentes — SID 1000005
Ce scénario représente une activité automatisée ou un volume inhabituel de requêtes web.

Comparer les alertes Suricata au nombre de requêtes Nginx sur la même période, à leur source et aux codes de réponse.

Le test est limité à 30 requêtes. Il ne démontre pas un déni de service.

Action suggérée : vérifier si le trafic est attendu et examiner son effet sur le service.

## Lecture des preuves Kibana

Pour chaque scénario, filtrer sur son SID dans la vue Projet sécurité :

    event_type : "alert" and alert.signature_id : 1000003

Adapter le SID au scénario et choisir une période couvrant le test.

Lire l’heure, la signature, les IP source et destination, le port et la sévérité. Le nombre de documents correspond à des événements enregistrés, pas nécessairement à autant d’attaques distinctes.

Dans la vue Journaux système et web, examiner les événements du service concerné sur la même période. La concordance des heures, des IP et des requêtes aide à relier les journaux ; une proximité temporelle seule ne suffit pas.

Les journaux Suricata sont prioritaires pour les cinq détections. Les journaux SSH apportent le contexte du scénario 2, et les journaux Nginx celui des scénarios 3 à 5. Un scan TCP peut ne produire aucun journal applicatif si aucune requête n’atteint l’application.
## Captures des cinq scénarios

Chaque capture présente le filtre du SID, la période sélectionnée et les résultats dans Kibana.

- [Scénario 1 — Scan TCP, SID 1000001](../captures/scenario-1-scan.jpeg)
- [Scénario 2 — Connexions SSH répétées, SID 1000002](../captures/scenario-2-ssh.jpeg)
- [Scénario 3 — Motif SQL, SID 1000003](../captures/scenario-3-sql.jpeg)
- [Scénario 4 — Parcours de chemin, SID 1000004](../captures/scenario-4-chemin.jpeg)
- [Scénario 5 — Requêtes HTTP fréquentes, SID 1000005](../captures/scenario-5-http.jpeg)

Pour lire ces preuves, vérifier le SID recherché, la période et les événements affichés. Les résultats montrent le déclenchement des règles ; ils ne prouvent pas une exploitation réussie.
## Dashboard de supervision

[Voir la capture du dashboard Supervision Suricata](../captures/dashboard-suricata.jpeg)

Le dashboard présente un tableau des alertes et un compteur. Le tableau permet de lire les heures, les IP source et destination et les signatures pour orienter l’analyse.

Sur la capture, le filtre `event_type : "alert"` est appliqué et le compteur affiche 118 événements sur la période sélectionnée. Ce total représente des alertes enregistrées, pas 118 attaques distinctes. Il dépend du filtre et de la période affichés.

Pour examiner un événement, relever ses informations puis rechercher les journaux correspondants dans Discover.
### Autres panneaux du dashboard

[Voir la chronologie, les signatures et les IP sources](../captures/dashboard-suricata-suite.jpeg)

- La chronologie permet de repérer les périodes concentrant les alertes.
- La répartition par signature permet de comparer les types de détections.
- La répartition par IP source permet d’identifier les sources générant le plus d’alertes.

Ces panneaux se lisent avec le filtre et la période sélectionnés. Une fréquence élevée d’alertes ne prouve pas, à elle seule, une compromission.
