# radio_service.py — Detailed Explanation (Line by Line)

## 1. Imports

from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import time

- http.server: creates a simple HTTP server
- BaseHTTPRequestHandler: handles incoming requests
- HTTPServer: runs the server
- subprocess: runs system commands (scripts, mpg123)
- json: formats responses
- time: used for delays

---

## 2. Network configuration

HOST = "0.0.0.0"
PORT = 9000

- 0.0.0.0: listen on all interfaces
- PORT: service port

---

## 3. Radio definitions

RADIOS = {
    "info": {
        "script": "/home/arduino/scripts/play_INFO.sh",
        "name": "France Info"
    }
}

- Maps URL → script + display name

Example:
GET /info → runs play_INFO.sh

---

## 4. Stop script

SCRIPT_STOP = "/home/arduino/scripts/stop_radio.sh"

- Stops any running stream

---

## 5. HTTP handler class

class RadioHandler(BaseHTTPRequestHandler):

Defines custom behavior for HTTP requests

---

## 6. Send JSON response

def _send_json(self, payload, status=200):

- Converts Python dict → JSON
- Sends HTTP response
- Adds headers (Content-Type, CORS)

---

## 7. Disable logs

def log_message(self, format, *args):
    return

- Prevents console spam

---

## 8. Start radio

def start_radio(self, script):

1. Stop current radio
2. Wait 1 second
3. Launch new script with subprocess.Popen

- Runs in background
- Logs redirected to /tmp

---

## 9. Handle GET requests

def do_GET(self):

path = self.path.strip("/")

### Cases:

- If path in RADIOS → start radio
- If "stop" → stop playback
- If "status" → check mpg123 process
- Else → return 404

---

## 10. Server start

if __name__ == "__main__":

HTTPServer((HOST, PORT), RadioHandler).serve_forever()

- Starts HTTP server
- Runs indefinitely

---

## Global Summary

WebUI → HTTP → radio_service.py → shell script → mpg123 → audio

This script acts as a bridge between App Lab and the Linux audio system.
