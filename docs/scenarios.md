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
L'utilisateur a confirmé zéro résultat. La sortie terminal horodatée avec HTTP 200 n'a pas été transmise ; conserver cette preuve pour clôturer le contrôle.
