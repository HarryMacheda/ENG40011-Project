
from DeviceApiClient.ApiClient import ApiClient
from StandardLibrary.PythonTypes import ColourAlert

API_BASE_URL = "http://127.0.0.1:8000"




async def main():
    client = ApiClient(API_BASE_URL)
    alert = ColourAlert(
        r = 255,
        g = 10,
        b = 20,
        isBlood= True
    )
    await client.sendLiquidDetected()
    await client.sendColour(alert)

import asyncio
asyncio.run(main())
