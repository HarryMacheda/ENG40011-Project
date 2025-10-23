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
        return alert
    
    if (alert.g < 0 or 158 < alert.g):
        return alert

    if (alert.b < 65 or 144 < alert.b):
        return alert
    
    #check norm diff
    diff = (alert.r - alert.g)/(alert.r + alert.g + 1)
    if (diff < 0.234 or 0.996 < diff):
        return alert
    
    diff = (alert.r - alert.b)/(alert.r + alert.b + 1)
    if (diff < 0.278 or 0.592 < diff):
        return alert

    #Check relative intensity
    relative = alert.r/alert.g
    if (relative < 1.604 or 255 < relative):
        return alert
    
    relative = alert.r/alert.b
    if (relative < 1.758 or 3.864 < relative):
        return alert


    alert.isBlood = True
    return alert

async def main():
    matrix = ColourSensorMatrix()
    client = ApiClient("https://192.168.1.185:8000")

    if not matrix.channels:
        print("No sensors detected")
        return

    sensor = LiquidSensor(pin=17)
    print("Beggining detection")
    while True:

        try:
            if not sensor.is_detected():
                continue
        
            try:
                await client.sendLiquidDetected(DEVICE_ROOM)
            except Exception as e:
                print(f"Error sending detection {e}")
                pass

            for i in range(matrix.channels.__len__() - 1):
                channel = matrix.channels[i]
                rgb = matrix.get_color(channel)

                print(f"Channel {channel}) colour: {rgb}")
                alert = ColourAlert(r=rgb[0], g=rgb[1], b=rgb[2], isBlood=False)
                alert = isBlood(alert)
                try:
                    print(alert)
                    await client.sendColour(DEVICE_ROOM, alert)
                    print(f"Colour sent to server for channel {channel} {alert}")
                    break
                except Exception as e:
                    print(f"Failed to send colour: {e}")
        except Exception as e:
            import traceback
            print(f"Error occured: {e}")
            traceback.print_exc()
        await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(main())
