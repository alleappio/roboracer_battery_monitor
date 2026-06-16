import sys

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from telemetry import Telemetry
import json

class Dashboard:
    def __init__(self, app, telemetry):
        self.app = app
        self.telemetry = telemetry
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/")
        async def read_root():
            with open("webapp/index.html", "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content, status_code=200)

        @self.app.get("/api/telemetry")
        def get_telemetry():
            return json.dumps(self.telemetry.read())
