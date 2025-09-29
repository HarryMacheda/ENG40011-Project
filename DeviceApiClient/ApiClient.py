from typing import Optional, Dict, Any, Union
from .RequestHandler import RequestHandler
from StandardLibrary.PythonTypes import Colour, ColourAlert

CLIENT_ID = "device_connector"
CLIENT_SECRET = "82b9e9e2558940df96a813ff69e7dfd4"

class ApiClient:
    def __init__(self, base_url: str):
        self.client = RequestHandler(base_url, headers={})
        self.token = None

    async def GetToken(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        response = await self.client.request("/auth/token", "POST", data, isForm=True)

        self.token = response["access_token"]
        self.client.headers["Authorization"] = "Bearer " + self.token
    
    async def sendColour(self, alert:ColourAlert):
        if self.token is None:
            await self.GetToken()

        await self.client.request("/liquid/colour", "POST", alert)

    async def sendLiquidDetected(self):
        if self.token is None:
            await self.GetToken()

        await self.client.request("/liquid/detected", "POST")

    