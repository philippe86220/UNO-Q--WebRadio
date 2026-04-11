# UNO Q Web Radio (App Lab + WebUI + Linux Host Audio)

## Objective

Create a web-controlled radio on the Arduino UNO Q using:

- App Lab (WebUI HTML Brick)
- Python backend (App Lab container)
- Linux host service for audio playback (`mpg123`)
- Internal communication via HTTP (`172.17.0.1`)

The goal is also to use a **USB sound card connected to a small speaker**,  
so that the MP3 stream from a web radio is **played directly through this speaker**.

---

## Audio Output Hardware

To enable sound playback from the web radio directly on the Arduino UNO Q, an external USB audio solution is required.
**USB Sound Card**
- Product link: https://www.amazon.fr/dp/B08Y8CZB2S  
- Role: Converts digital audio from the UNO Q (Linux side) into an analog signal (3.5 mm jack output)
- Output: Connects to a small speaker or headphones
This is essential because the UNO Q does not provide a native audio output.

---

**USB Hub**
- Product link: https://www.amazon.fr/dp/B0CF224WX9
- Role: Expands the USB connectivity of the UNO Q
- Usage:
  - Connect the USB sound card
  - Optionally connect other peripherals (keyboard, storage, etc.)
  - 
The USB hub is required because the UNO Q has limited USB ports.

---

## Audio Output

Audio is not generated inside App Lab, but on the Linux system of the UNO Q.

The audio flow is as follows:

- `mpg123` reads the MP3 radio stream
- ALSA sends the audio to the sound card
- The **USB audio device** outputs the sound to the speaker

This provides a **fully autonomous audio output**, directly from the UNO Q.

---

## Architecture

```
WebUI (HTML - App Lab)
↓
App Lab Python (WebUI API)
↓
HTTP (172.17.0.1:9000)
↓
radio_service.py (Linux host)
↓
Shell scripts
↓
mpg123 + ALSA
↓
Audio output (USB / Jack)
```
---

## Understanding the Architecture (Beginner Friendly)

This project uses two separate environments on the UNO Q:

1. **App Lab (container)**  
   - Runs the WebUI (HTML interface)  
   - Runs Python backend (`main.py`)  
   - Cannot directly access hardware or Linux system tools  

2. **Linux host (UNO Q system)**  
   - Runs `radio_service.py`  
   - Has access to audio hardware (ALSA)  
   - Executes `mpg123` to play radio streams  

---

## Role of `radio_service.py`

`radio_service.py` is the **bridge between App Lab and the audio system**.

### What it does:

- Listens on port `9000`
- Receives HTTP requests such as:
  - `/info`
  - `/rtl`
  - `/inter`
  - `/musique`
- Stops any currently playing stream
- Launches the correct shell script
- Starts audio playback using `mpg123`

### Why it is necessary:

App Lab runs inside a **container**, which means:
- it cannot directly execute Linux commands
- it cannot access ALSA or audio devices

Therefore, `radio_service.py` runs **outside App Lab**, on the Linux host, and acts as a **controlled entry point** to the system.

---

## Data Flow Explained

```
User clicks button (WebUI)
↓
HTML calls /api/info (App Lab)
↓
main.py (App Lab) forwards request
↓
HTTP request to 172.17.0.1:9000/info
↓
radio_service.py (Linux host)
↓
Shell script execution
↓
mpg123 reads radio stream
↓
ALSA outputs sound
```

---

## Project Structure

### App Lab

```
python/
main.py
assets/
index.html
```

### Linux host

```
/home/arduino/scripts/
radio_service.py
play_INFO.sh
play_RTL.sh
play_INTER.sh
play_MUSIQUE.sh
stop_radio.sh
```
---

## Linux Host Setup

### Install mpg123

```
sudo apt update
sudo apt install mpg123
```

---

**Example script**

```
#!/bin/sh
/usr/bin/mpg123 -o alsa -a hw:0,0 --buffer 4096 "http://icecast.radiofrance.fr/franceinfo-lofi.mp3"
```
make executable :

```
chmod +x /home/arduino/scripts/*.sh
```
---

Host Service (radio_service.py)
- Runs on port 9000
- Handles:
  - `/info`
  - `/rtl`
  - `/inter`
  - `/musique`
  - `/stop`
  - `/status`

code `/home/arduino/scripts/radio_service.py` :

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import time

HOST = "0.0.0.0"
PORT = 9000

RADIOS = {
    "info": {
        "script": "/home/arduino/scripts/play_INFO.sh",
        "name": "France Info"
    },
    "rtl": {
        "script": "/home/arduino/scripts/play_RTL.sh",
        "name": "RTL"
    },
    "inter": {
        "script": "/home/arduino/scripts/play_INTER.sh",
        "name": "France Inter"
    },
    "musique": {
        "script": "/home/arduino/scripts/play_MUSIQUE.sh",
        "name": "France Musique"
    }
}

SCRIPT_STOP = "/home/arduino/scripts/stop_radio.sh"

class RadioHandler(BaseHTTPRequestHandler):

    def _send_json(self, payload, status=200):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return

    def start_radio(self, script):
        subprocess.run([SCRIPT_STOP])
        time.sleep(1.0)

        subprocess.Popen(
            [script],
            stdout=open("/tmp/radio_stdout.log", "a"),
            stderr=open("/tmp/radio_stderr.log", "a"),
            start_new_session=True
        )

    def do_GET(self):

        path = self.path.strip("/")

        if path in RADIOS:
            self.start_radio(RADIOS[path]["script"])
            self._send_json({
                "ok": True,
                "station": RADIOS[path]["name"]
            })
            return

        if path == "stop":
            subprocess.run([SCRIPT_STOP])
            self._send_json({"ok": True, "station": "stopped"})
            return

        if path == "status":
            result = subprocess.run(
                ["pgrep", "-f", "mpg123"],
                capture_output=True,
                text=True
            )
            running = (result.returncode == 0)
            self._send_json({"ok": True, "running": running})
            return

        self._send_json({"ok": False, "error": "Not found"}, status=404)


if __name__ == "__main__":
    print(f"Radio service listening on {HOST}:{PORT}")
    HTTPServer((HOST, PORT), RadioHandler).serve_forever()
```

---

**Auto-start with systemd**

Create service:

```
sudo nano /etc/systemd/system/radio_service.service
```

```
[Unit]
Description=UNO Q radio service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=arduino
WorkingDirectory=/home/arduino/scripts
ExecStart=/usr/bin/python3 /home/arduino/scripts/radio_service.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:

```
sudo systemctl daemon-reload
sudo systemctl enable radio_service.service
sudo systemctl start radio_service.service
```
---

Test

```
curl http://127.0.0.1:9000/status
curl http://127.0.0.1:9000/info
```

---

**App Lab (main.py)**

Uses WebUI Brick:
- exposes `/api/...`
- proxies requests to host
  
Example:

```python
ui.expose_api("GET", "/api/info", lambda: proxy_get("/info"))
```
---

**WebUI**

- HTML interface
- buttons:
  -France Info
  - RTL
  -France Inter
  -France Musique
- calls `/api/...`

---

**Important Notes**

- App Lab runs in a container
- Cannot directly access host scripts
- Must use HTTP bridge (172.17.0.1)

---

**Debug**

Check service:

```
sudo systemctl status radio_service.service
```

Logs:

```
journalctl -u radio_service.service -n 50 --no-pager
```

---

**Result**

- Fully autonomous web radio
- Starts at boot
- Controlled via App Lab WebUI
- Clean separation between UI and audio engine

  ---

**Author Notes**

Tested on Arduino UNO Q
Using App Lab + WebUI HTML Brick

---

## Acknowledgments

This project was developed with the help of ChatGPT,  
which assisted with:

- architecture design (App Lab ↔ Linux host)
- debugging Python and systemd service
- improving code structure and reliability

The final implementation and testing were done on real hardware (UNO Q).

