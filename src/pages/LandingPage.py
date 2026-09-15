from src import ASSETS, THEME

from src.pages.SettingsPage import SettingsPage
from src.pages.StaticPage import StaticPage
from src.pages.AudiobookshelfLandingPage import AudiobookshelfLandingPage

class LandingPage(StaticPage, img_path=ASSETS / "landing.png"):
    # img_path = ASSETS / "landing.png"

    async def center_pressed(self):
        # self.draw.rectangle((10, 10, self.width-20, self.height-20), outline=0, fill=0)
        self.draw.text((10, 10), "Hello World", fill=THEME["text_color"])
        return True

    async def left_pressed(self):
        return 'Settings'

    async def right_pressed(self):
        return 'AudiobookshelfLanding'
