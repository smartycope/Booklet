from src.pages.Page import Page
from PIL import Image
from src.aobject import aobject

class StaticPage(Page, aobject):
    async def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __init_subclass__(cls, img_path, **kwargs):
        cls.img_path = img_path
        super().__init_subclass__(**kwargs)
        return cls

    def first_image(self):
        return Image.open(self.img_path)
