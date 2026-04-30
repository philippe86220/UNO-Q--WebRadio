from urllib.request import urlopen
import json

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI

import requests

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

def api_volume(value: int):
    value = int(value)

    if value < 0:
        value = 0
    if value > 100:
        value = 100

    r = requests.get(f"{HOST_SERVICE}/volume?value={value}", timeout=2)
    return r.json()


# routes
ui.expose_api("GET", "/api/info", lambda: api_radio("info"))
ui.expose_api("GET", "/api/rtl", lambda: api_radio("rtl"))
ui.expose_api("GET", "/api/inter", lambda: api_radio("inter"))
ui.expose_api("GET", "/api/musique", lambda: api_radio("musique"))
ui.expose_api("GET", "/api/nostalgie", lambda: api_radio("nostalgie"))
ui.expose_api("GET", "/api/mradio", lambda: api_radio("mradio"))
ui.expose_api("GET", "/api/volume", api_volume)
ui.expose_api("GET", "/api/stop", api_stop)
ui.expose_api("GET", "/api/status", api_status)

App.run()
