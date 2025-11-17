from .Page import Page
from PIL import Image

class StaticPage(Page):
    def first_image(self):
        return Image.open(self.img_path)


