from .StaticPage import StaticPage

class LandingPage(StaticPage):
    img_path = "../assets/icon.png"

    def center_pressed(self):
        # self.draw.rectangle((10, 10, self.width-20, self.height-20), outline=0, fill=0)
        self.draw.text((10, 10), "Hello World", fill=0)
        return True

    def down_pressed(self):
        return 'test'