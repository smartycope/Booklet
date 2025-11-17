from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from globals import WIDTH, HEIGHT, THEME

class Page(ABC):
    width = WIDTH
    height = HEIGHT

    def __init__(self):
        self.img = self.first_image()
        self.draw = ImageDraw.Draw(self.img)

    def first_image(self):
        return Image.new("RGB", (self.width, self.height), THEME["bg"])

    def up_pressed(self): pass
    def down_pressed(self): pass
    def left_pressed(self): pass
    def right_pressed(self): pass
    def center_pressed(self): pass
    def key1_pressed(self): pass
    def key2_pressed(self): pass
    def key3_pressed(self): pass

    def up_released(self): pass
    def down_released(self): pass
    def left_released(self): pass
    def right_released(self): pass
    def center_released(self): pass
    def key1_released(self): pass
    def key2_released(self): pass
    def key3_released(self): pass

    def up_held(self): pass
    def down_held(self): pass
    def left_held(self): pass
    def right_held(self): pass
    def center_held(self): pass
    def key1_held(self): pass
    def key2_held(self): pass
    def key3_held(self): pass
