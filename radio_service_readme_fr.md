# radio_service.py — Explication détaillée ligne par ligne

## 1. Imports

from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import time
from urllib.parse import urlparse, parse_qs

- http.server : crée un serveur HTTP simple
- BaseHTTPRequestHandler : gère les requêtes entrantes
- HTTPServer : moteur du serveur
- subprocess : exécute des commandes système (scripts, mpg123)
- json : formate les réponses en JSON
- time : permet de faire des pauses
- urllib.parse : permet d’analyser l’URL et les paramètres

---

## 2. Configuration réseau

HOST = "0.0.0.0"
PORT = 9000

- 0.0.0.0 : écoute sur toutes les interfaces réseau
- PORT : port du service

---

## 2.1 Configuration du volume

CARD = "0"
VOLUME_NUMID = "3"

- CARD : numéro de la carte son ALSA
- VOLUME_NUMID : contrôle ALSA utilisé pour le volume

Exemple :

amixer -c 0 cset numid=3 50%

---

## 3. Définition des radios

RADIOS = { ... }

- Associe une URL à un script

Exemple :
GET /info → lance play_INFO.sh

---

## 4. Script d’arrêt

SCRIPT_STOP = "/home/arduino/scripts/stop_radio.sh"

- Arrête toute lecture audio

---

## 5. Classe principale

class RadioHandler(BaseHTTPRequestHandler):

- Gère les requêtes HTTP

---

## 6. Envoi JSON

def _send_json(self, payload, status=200):

- Convertit en JSON
- Envoie la réponse HTTP
- Ajoute les headers (CORS, etc.)

---

## 7. Désactivation des logs

def log_message(self, format, *args):
    return

- Supprime les logs console

---

## 8. Lancer une radio

def start_radio(self, script):

1. Stoppe la radio en cours
2. Attend 1 seconde
3. Lance le script avec subprocess.Popen

- Exécution en arrière-plan
- Logs dans /tmp

---

## 8.1 Gestion du volume

def set_volume(self, value):

- Convertit la valeur reçue en entier
- Si erreur → valeur par défaut = 50
- Limite la valeur entre 0 et 100
- Applique le volume avec amixer
- Retourne la valeur appliquée

---

## 9. Gestion GET

def do_GET(self):

- Analyse l’URL et les paramètres

Cas :
- /info → lance radio
- /volume?value=XX → règle le volume
- /stop → stop
- /status → vérifie mpg123
- sinon → erreur 404

Exemple :
GET /volume?value=70

→ règle le volume à 70%

---

## 10. Lancement serveur

if __name__ == "__main__":

HTTPServer((HOST, PORT), RadioHandler).serve_forever()

- Démarre le serveur HTTP

---

## Résumé

WebUI → App Lab → HTTP → radio_service.py → amixer / script → mpg123 → audio

Ce script fait le lien entre App Lab et le système Linux.
