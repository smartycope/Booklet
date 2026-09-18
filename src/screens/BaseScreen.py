from abc import ABC, abstractmethod
from gpiozero import Button
import atexit

from src import CONFIG
try:
    from globals import WIDTH, HEIGHT
# For test scripts -- can be removed eventually
except ImportError:
    from src import WIDTH, HEIGHT

class BaseScreen(ABC):
    KEY_UP_PIN    = 6
    KEY_DOWN_PIN  = 19
    KEY_LEFT_PIN  = 5
    KEY_RIGHT_PIN = 26
    KEY_CENTER_PIN= 13

    KEY1_PIN      = 21
    KEY2_PIN      = 20
    KEY3_PIN      = 16

    width  = WIDTH
    height = HEIGHT

    hold_time = .2

    @property
    def brightness(self):
        return CONFIG['brightness']

    @brightness.setter
    def brightness(self, value):
        CONFIG['brightness'] = value
        CONFIG.sync()

    def __init__(self, brightness=1):
        self._display_awake = True
        self.gpio_key_up_pin    = Button(self.KEY_UP_PIN, pull_up=True, active_state=None, hold_time=self.hold_time, hold_repeat=True)
        self.gpio_key_down_pin  = Button(self.KEY_DOWN_PIN, pull_up=True, active_state=None, hold_time=self.hold_time, hold_repeat=True)
        self.gpio_key_left_pin  = Button(self.KEY_LEFT_PIN, pull_up=True, active_state=None, hold_time=self.hold_time, hold_repeat=True)
        self.gpio_key_right_pin = Button(self.KEY_RIGHT_PIN, pull_up=True, active_state=None, hold_time=self.hold_time, hold_repeat=True)
        self.gpio_key_center_pin= Button(self.KEY_CENTER_PIN, pull_up=True, active_state=None)

        self.gpio_key1_pin      = Button(self.KEY1_PIN, pull_up=True, active_state=None)
        self.gpio_key2_pin      = Button(self.KEY2_PIN, pull_up=True, active_state=None)
        self.gpio_key3_pin      = Button(self.KEY3_PIN, pull_up=True, active_state=None)

        self.brightness = brightness

        atexit.register(self.close)

    def sleep(self):
        self._display_awake = False
        backlight = getattr(self, "gpio_bl_pin", None)
        if backlight is not None:
            backlight.off()

    def wake(self):
        self._display_awake = True
        backlight = getattr(self, "gpio_bl_pin", None)
        if backlight is not None:
            backlight.value = self.brightness / 2

    @abstractmethod
    def close(self): pass

    @abstractmethod
    def show_image(self, image, x_start=0, y_start=0, x_end=None, y_end=None): pass

    @abstractmethod
    async def listen(self): pass
