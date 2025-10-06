from gpiozero import Button

class LiquidSensor:
    def __init__(self, pin: int = 17, pull_up: bool = False):
        self.probe = Button(pin, pull_up=pull_up)

    def is_detected(self) -> bool:
        return self.probe.is_pressed