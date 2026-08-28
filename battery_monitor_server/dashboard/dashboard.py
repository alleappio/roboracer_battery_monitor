import sys

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from telemetry import Telemetry
import json

class Dashboard:
    def __init__(self, telemetry):
        self.app = FastAPI()
        self.telemetry = telemetry
        self.setup_routes()

    def setup_routes(self):
        self.app.mount("/static", StaticFiles(directory="webapp"), name="static")

        @self.app.get("/health")
        def health():
            return {"status": "ok"}

        @self.app.get("/")
        def read_root():
            with open("webapp/index.html", "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content, status_code=200)

        @self.app.get("/api/telemetry/smooth")
        def get_telemetry():
            return json.dumps(self.telemetry.read())

        @self.app.get("/api/telemetry/raw")
        def get_telemetry():
            return json.dumps(self.telemetry.read_raw())
