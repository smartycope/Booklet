from abc import ABC, abstractmethod
from gpiozero import Button
import atexit
from globals import WIDTH, HEIGHT

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

    def __init__(self):
        self.gpio_key_up_pin    = Button(self.KEY_UP_PIN, pull_up=True, active_state=None)
        self.gpio_key_down_pin  = Button(self.KEY_DOWN_PIN, pull_up=True, active_state=None)
        self.gpio_key_left_pin  = Button(self.KEY_LEFT_PIN, pull_up=True, active_state=None)
        self.gpio_key_right_pin = Button(self.KEY_RIGHT_PIN, pull_up=True, active_state=None)
        self.gpio_key_center_pin= Button(self.KEY_CENTER_PIN, pull_up=True, active_state=None)

        self.gpio_key1_pin      = Button(self.KEY1_PIN, pull_up=True, active_state=None)
        self.gpio_key2_pin      = Button(self.KEY2_PIN, pull_up=True, active_state=None)
        self.gpio_key3_pin      = Button(self.KEY3_PIN, pull_up=True, active_state=None)

        atexit.register(self.close)

    @abstractmethod
    def close(self): pass

    @abstractmethod
    def show_image(self, image): pass

    @abstractmethod
    def listen(self): pass