from src.pages.BarLevelPage import BarLevelPage


class BrightnessPage(BarLevelPage):
    def __init__(self):
        super().__init__(
            title="Brightness",
            level=1.0,
            right_pressed="settings",
        )

    def set_level(self, level: float):
        if super().set_level(level):
            BrightnessPage.screen.brightness = level
            return True
