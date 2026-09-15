from src import CONFIG
from src.pages.BarLevelPage import BarLevelPage
from src.pages.SettingsPage import SettingsPage

class BrightnessPage(BarLevelPage):
    async def __init__(self):
        await super().__init__(
            title="Brightness",
            level=CONFIG.get('brightness', 1.0),
        )

    def set_level(self, level: float):
        if super().set_level(level):
            self.manager.screen.brightness = level
            return True

    async def right_pressed(self):
        return 'Settings'
