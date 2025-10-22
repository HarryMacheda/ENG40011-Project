# DeviceApiClientFolder/main.py

import asyncio
from DeviceApiClient.ApiClient import ApiClient
from Sensors.LiquidSensor import LiquidSensor
from Sensors.ColourSensorMatrix import ColourSensorMatrix
from StandardLibrary.PythonTypes import ColourAlert

DEVICE_ROOM = "101A"

def isBlood(alert: ColourAlert):
    #Check raw range
    if (alert.r != 255):
        return
    
    if (alert.g < 0 or 158 < alert.g):
        return

    if (alert.b < 65 or 144 < alert.b):
        return
    
    #check norm diff
    diff = (alert.r - alert.g)/(alert.r + alert.g + 1)
    if (diff < 0.234 or 0.996 < diff):
        return
    
    diff = (alert.r - alert.b)/(alert.r + alert.b + 1)
    if (diff < 0.278 or 0.592 < diff):
        return

    #Check relative intensity
    relative = alert.r/alert.g
    if (relative < 1.604 or 255 < relative):
        return
    
    relative = alert.r/alert.b
    if (relative < 1.758 or 3.864 < relative):
        return


    alert.isBlood = True

async def main():
    matrix = ColourSensorMatrix()
    client = ApiClient("http://192.168.1.143:8000")

    if not matrix.channels:
        print("No sensors detected")
        return

    sensor = LiquidSensor(pin=17)

    while True:

        if not sensor.is_detected():
            return
        
        try:
            await client.sendLiquidDetected(DEVICE_ROOM)
        except Exception as e:
            pass

        for i in range(matrix.channels.__len__ - 1):
            channel = matrix.channels[i]

            print(f"Channel {channel}) colour: {rgb}")
            rgb = matrix.get_color(channel)
            alert = ColourAlert(r=rgb[0], g=rgb[1], b=rgb[2], isBlood=False)
            alert = isBlood(alert)

            try:
                await client.sendColour(DEVICE_ROOM, alert)
                print(f"Colour sent to server for channel {channel}")
                break
            except Exception as e:
                print(f"Failed to send colour: {e}")
        
        await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(main())
