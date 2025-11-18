from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from src.constants import WIDTH, HEIGHT, THEME

class Page(ABC):
    width = WIDTH
    height = HEIGHT

    def __init__(self, **goto_page):
        self.img = self.first_image()
        self.draw = ImageDraw.Draw(self.img)

        for key, value in goto_page.items():
            setattr(self, key, lambda: value)

    def first_image(self):
        return Image.new("RGB", (self.width, self.height), THEME["bg"])

    def text(self, text, x, y, inverted=False, font=THEME['font'], fill=None):
        fill = fill or THEME['bg' if inverted else 'text_color']
        self.draw.text((x, y), text, font=font, fill=fill)
        return self.draw.textbbox((x, y), text, font=font)

    @staticmethod
    def combine_bbox(bbox1, bbox2):
        """ Combine two bounding boxes, returning the smallest box that contains both """
        return (
            min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),
            max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])
        )

    def reset_img(self):
        self.img = self.first_image()
        self.draw = ImageDraw.Draw(self.img)

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

