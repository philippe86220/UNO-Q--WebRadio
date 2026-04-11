from urllib.request import urlopen
import json

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()

HOST_SERVICE = "http://172.17.0.1:9000"

def proxy_get(path: str):
    try:
        with urlopen(HOST_SERVICE + path, timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}

def api_radio(name):
    return proxy_get(f"/{name}")

def api_stop():
    return proxy_get("/stop")

def api_status():
    return proxy_get("/status")

# routes
ui.expose_api("GET", "/api/info", lambda: api_radio("info"))
ui.expose_api("GET", "/api/rtl", lambda: api_radio("rtl"))
ui.expose_api("GET", "/api/inter", lambda: api_radio("inter"))
ui.expose_api("GET", "/api/musique", lambda: api_radio("musique"))

ui.expose_api("GET", "/api/stop", api_stop)
ui.expose_api("GET", "/api/status", api_status)

App.run()
