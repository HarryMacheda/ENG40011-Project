# DeviceApiClientFolder/main.py

import asyncio
from DeviceApiClient.ApiClient import ApiClient
from Sensors.ColourSensorMatrix import ColourSensorMatrix
from StandardLibrary.PythonTypes import ColourAlert

async def main():
    matrix = ColourSensorMatrix()
    client = ApiClient("http://192.168.1.143:8000")

    if not matrix.channels:
        print("No sensors detected")
        return

    first_channel = matrix.channels[0]

    while True:
        rgb = matrix.get_color(first_channel)
        print(f"First sensor (channel {first_channel}) colour: {rgb}")

        alert = ColourAlert(r=rgb[0], g=rgb[1], b=rgb[2], isBlood=False)

        try:
            await client.sendColour(alert)
            print(f"Colour sent to server for channel {first_channel}")
        except Exception as e:
            print(f"Failed to send colour: {e}")

        await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(main())
