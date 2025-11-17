from .StaticPage import StaticPage
from PIL import Image

class TestPage(StaticPage):
    img_path = "../../assets/icon.png"

    def first_image(self):
        return Image.new("RGB", (self.width, self.height), "#FFEFD7")

    def center_pressed(self):
        self.draw.rectangle((25, 25, self.width-50, self.height-50), outline=0, fill=0)
        return True

    def up_pressed(self):
        return 'landing'
