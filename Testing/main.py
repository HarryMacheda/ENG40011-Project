# DeviceApiClientFolder/main_emulated_devices.py

import asyncio
import random
from DeviceApiClient.ApiClient import ApiClient
from StandardLibrary.PythonTypes import ColourAlert

# Emulated sensors
class LiquidSensor:
    def __init__(self, pin):
        self.pin = pin

    def is_detected(self):
        return random.random() < 0.005


class ColourSensorMatrix:
    def __init__(self, num_channels=1):
        self.channels = list(range(num_channels))

    def get_color(self, channel):
        base_color = random.choices(
            ["white", "red", "yellow"],
            weights=[99, 1, 1],
            k=1
        )[0]
        
        intensity = random.uniform(0.5, 1.0)
        
        if base_color == "red":
            r = int(random.randint(180, 255) * intensity)  # strong red
            g = int(random.randint(0, 100) * intensity)    # low green
            b = int(random.randint(0, 80) * intensity)     # low blue
        elif base_color == "yellow":
            r = int(random.randint(180, 255) * intensity)  # strong red
            g = int(random.randint(180, 255) * intensity)  # strong green
            b = int(random.randint(0, 80) * intensity)     # low blue
        else:  # white
            r = int(random.randint(250, 255))
            g = int(random.randint(250, 255))
            b = int(random.randint(250, 255))

        return [r, g, b]

ROOMS = [ "101B",
    "102A", "102B",
    "103A", "103B",
    "104A", "104B",
    "105A", "105B",
    "106A", "106B",
    "107A", "107B",
    "108A", "108B",
    "109A", "109B",
    "110A", "110B"
]

SENSORS_PER_DEVICE = 1             


async def sensor_loop(room, channel, sensor, matrix, client):
    while True:
        if sensor.is_detected():
            try:
                await client.sendLiquidDetected(room)
            except Exception as e:
                print(f"[Room {room} | Channel {channel}] Failed to send liquid detection: {e}")

        rgb = matrix.get_color(channel)
        alert = ColourAlert(r=rgb[0], g=rgb[1], b=rgb[2], isBlood=False)
        try:
            await client.sendColour(room, alert)
        except Exception as e:
            print(f"[Room {room} | Channel {channel}] Failed to send colour: {e}")

        await asyncio.sleep(1)


async def device_loop(room):
    matrix = ColourSensorMatrix(num_channels=SENSORS_PER_DEVICE)
    client = ApiClient("https://192.168.1.143:8000")
    tasks = []

    for channel in matrix.channels:
        sensor = LiquidSensor(pin=17 + channel)  
        tasks.append(asyncio.create_task(sensor_loop(room, channel, sensor, matrix, client)))

    await asyncio.gather(*tasks)


async def main():
    device_tasks = [asyncio.create_task(device_loop(room)) for room in ROOMS]
    await asyncio.gather(*device_tasks)


if __name__ == "__main__":
    asyncio.run(main())
