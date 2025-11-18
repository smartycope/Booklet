from src.constants import ASSETS, THEME

from src.pages.StaticPage import StaticPage


class LandingPage(StaticPage):
    img_path = ASSETS / "landing.png"

    def center_pressed(self):
        # self.draw.rectangle((10, 10, self.width-20, self.height-20), outline=0, fill=0)
        self.draw.text((10, 10), "Hello World", fill=THEME["text_color"])
        return True

    def down_pressed(self):
        return 'settings'

    def left_pressed(self):
        return 'spotify playlist'

    def right_pressed(self):
        return 'audiobookshelf landing'
