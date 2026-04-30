# radio_service.py — Detailed Explanation (Line by Line)

## 1. Imports

from http.server import BaseHTTPRequestHandler, HTTPServer  
import subprocess  
import json  
import time  
from urllib.parse import urlparse, parse_qs  

- http.server: creates a simple HTTP server  
- BaseHTTPRequestHandler: handles incoming requests  
- HTTPServer: runs the server  
- subprocess: runs system commands (scripts, mpg123)  
- json: formats responses  
- time: used for delays  
- urllib.parse: parses URL and query parameters  

---

## 2. Network configuration

HOST = "0.0.0.0"  
PORT = 9000  

- 0.0.0.0: listen on all interfaces  
- PORT: service port  

---

## 2.1 Volume configuration

CARD = "0"  
VOLUME_NUMID = "3"  

Defines the ALSA sound card and the mixer control used for volume.

Example command:

amixer -c 0 cset numid=3 50%

---

## 3. Radio definitions

RADIOS = { ... }

Maps URL → script + display name

Example:  
GET /info → runs play_INFO.sh  

---

## 4. Stop script

SCRIPT_STOP = "/home/arduino/scripts/stop_radio.sh"

Stops any running stream  

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

def log_message(self, format, *args): return

Prevents console spam  

---

## 8. Start radio

def start_radio(self, script):

- Stop current radio  
- Wait 1 second  
- Launch new script with subprocess.Popen  
- Runs in background  
- Logs redirected to /tmp  

---

## 8.1 Set volume

def set_volume(self, value):

- Converts the received value to an integer  
- If invalid → default = 50  
- Clamps value between 0 and 100  
- Calls `amixer` to apply volume  
- Returns applied volume  

---

## 9. Handle GET requests

def do_GET(self):

The request path and query parameters are parsed:

parsed = urlparse(self.path)  
path = parsed.path.strip("/")  
query = parse_qs(parsed.query)  

Cases:

- if path in RADIOS → start radio  
- if path == "volume" → set volume using `value` parameter  
- if path == "stop" → stop playback  
- if path == "status" → check mpg123 process  
- else → return 404  

Example:

GET /volume?value=70  

Sets volume to 70%.

---

## 10. Server start

if __name__ == "__main__":

HTTPServer((HOST, PORT), RadioHandler).serve_forever()

- Starts HTTP server  
- Runs indefinitely  

---

## Global Summary

WebUI → App Lab → HTTP → radio_service.py → amixer / shell scripts → USB sound card  

This script acts as a bridge between App Lab and the Linux audio system.
