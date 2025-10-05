# DeviceApiClientFolder/main.py

import asyncio
from DeviceApiClient.ApiClient import ApiClient
from Sensors.ColourSensorMatrix import ColourSensorMatrix
from StandardLibrary.PythonTypes import ColourAlert

async def main():
    # Initialize the sensor matrix and API client once
    matrix = ColourSensorMatrix()
    client = ApiClient("http://192.168.1.143:8000")

    if not matrix.channels:
        print("No sensors detected")
        return

    first_channel = matrix.channels[0]

    while True:
        # Read the first sensor
        rgb = matrix.get_color(first_channel)  # [R, G, B] as 8-bit integers
        print(f"First sensor (channel {first_channel}) colour: {rgb}")

        # Prepare ColourAlert
        alert = ColourAlert(r=rgb[0], g=rgb[1], b=rgb[2], isBlood=False)

        # Send the colour to the server
        try:
            await client.sendColour(alert)
            print(f"Colour sent to server for channel {first_channel}")
        except Exception as e:
            print(f"Failed to send colour: {e}")

        # Wait a bit before the next reading
        await asyncio.sleep(1)  # 0.5 seconds between readings

if __name__ == "__main__":
    asyncio.run(main())
