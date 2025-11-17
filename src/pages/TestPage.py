from .StaticPage import StaticPage
from PIL import Image
from globals import ASSETS, THEME

class TestPage(StaticPage):
    img_path = ASSETS / "icon.png"

    def first_image(self):
        return Image.new("RGB", (self.width, self.height), THEME["bg"])

    def center_pressed(self):
        self.draw.rectangle((25, 25, self.width-50, self.height-50), outline=THEME["text_color"], fill=THEME["text_color"])
        return True

    def up_pressed(self):
        return 'landing'
