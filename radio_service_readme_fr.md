# radio_service.py — Explication détaillée ligne par ligne

## 1. Imports

from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import time

- http.server : crée un serveur HTTP simple
- BaseHTTPRequestHandler : gère les requêtes entrantes
- HTTPServer : moteur du serveur
- subprocess : exécute des commandes système (scripts, mpg123)
- json : formate les réponses en JSON
- time : permet de faire des pauses

---

## 2. Configuration réseau

HOST = "0.0.0.0"
PORT = 9000

- 0.0.0.0 : écoute sur toutes les interfaces réseau
- PORT : port du service

---

## 3. Définition des radios

RADIOS = {
    "info": {
        "script": "/home/arduino/scripts/play_INFO.sh",
        "name": "France Info"
    }
}

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

## 9. Gestion GET

def do_GET(self):

- Analyse l’URL

Cas :
- /info → lance radio
- /stop → stop
- /status → vérifie mpg123
- sinon → erreur 404

---

## 10. Lancement serveur

if __name__ == "__main__":

HTTPServer((HOST, PORT), RadioHandler).serve_forever()

- Démarre le serveur HTTP

---

## Résumé

WebUI → HTTP → radio_service.py → script → mpg123 → audio

Ce script fait le lien entre App Lab et le système Linux.
