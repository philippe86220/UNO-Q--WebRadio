from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import time
from urllib.parse import urlparse, parse_qs

HOST = "0.0.0.0"
PORT = 9000

CARD = "0"
VOLUME_NUMID = "3"

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
    },
    "nostalgie": {
        "script": "/home/arduino/scripts/play_NOSTALGIE.sh",
        "name": "Nostalgie"
    },
    "mradio": {
        "script": "/home/arduino/scripts/play_mRadioTop50.sh",
        "name": "M Radio Top 50"
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

    def set_volume(self, value):
        try:
            volume = int(value)
        except ValueError:
            volume = 50

        if volume < 0:
            volume = 0

        if volume > 100:
            volume = 100

        subprocess.run(
            ["amixer", "-c", CARD, "cset", f"numid={VOLUME_NUMID}", f"{volume}%"],
            capture_output=True,
            text=True
        )

        return volume

    def do_GET(self):

        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        query = parse_qs(parsed.query)

        if path in RADIOS:
            self.start_radio(RADIOS[path]["script"])
            self._send_json({
                "ok": True,
                "station": RADIOS[path]["name"]
            })
            return

        if path == "volume":
            value = query.get("value", ["50"])[0]
            volume = self.set_volume(value)

            self._send_json({
                "ok": True,
                "volume": volume
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

