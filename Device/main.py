# DeviceApiClientFolder/main.py

import asyncio
from DeviceApiClient.ApiClient import ApiClient
from Sensors.LiquidSensor import LiquidSensor
from Sensors.ColourSensorMatrix import ColourSensorMatrix
from StandardLibrary.PythonTypes import ColourAlert

DEVICE_ROOM = "101A"

async def main():
    matrix = ColourSensorMatrix()
    client = ApiClient("http://192.168.1.143:8000")

    if not matrix.channels:
        print("No sensors detected")
        return

    first_channel = matrix.channels[0]
    sensor = LiquidSensor(pin=17)

    while True:

        if(sensor.is_detected()):
            try:
                await client.sendLiquidDetected(DEVICE_ROOM)
            except Exception as e:
                pass

        rgb = matrix.get_color(first_channel)
        print(f"First sensor (channel {first_channel}) colour: {rgb}")

        alert = ColourAlert(r=rgb[0], g=rgb[1], b=rgb[2], isBlood=False)

        try:
            await client.sendColour(DEVICE_ROOM, alert)
            print(f"Colour sent to server for channel {first_channel}")
        except Exception as e:
            print(f"Failed to send colour: {e}")

        await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(main())
