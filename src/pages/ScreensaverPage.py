from PIL import Image, ImageDraw

from src.pages.Page import Page


class ScreensaverPage(Page):
    """Black placeholder displayed while the physical display is asleep."""

    def __init__(self, previous_page: Page):
        self.previous_page = previous_page
        self.img = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.img)
