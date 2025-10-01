from typing import Optional, Dict, Any, Union, List
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

    def isBloodDetected(self, linear_rgb: list[int]) -> bool:
        r, g, b = linear_rgb
        
        r_min, r_max = 150, 255
        g_min, g_max = 0, 80
        b_min, b_max = 0, 80
    
        return r_min <= r <= r_max and g_min <= g <= g_max and b_min <= b <= b_max
                 
    async def receiveColour(self, channel: int, linear_rgb: List[int]) -> ColourAlert:
        alert = ColourAlert(channel=channel, linear_rgb=linear_rgb)
        return alert
    
    
    async def sendColour(self, alert: ColourAlert):
        if self.token is None:
            await self.GetToken()
        await self.client.request("/liquid/colour", "POST", alert.dict())

    async def sendBloodDetected(self, channel: int, linear_rgb: list[int]) -> BloodAlert:
        if self.token is None:
            await self.GetToken()
        
        is_blood = self.is_blood_detected(linear_rgb)
        blood_alert = BloodAlert(channel=channel, isBlood=is_blood)
        
        if is_blood:
            await self.client.request("/liquid/blood", "POST", blood_alert.dict())
        
        return blood_alert

    
