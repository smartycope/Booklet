from src import CONFIG
from src.pages.BarLevelPage import BarLevelPage
from src.pages.SettingsPage import SettingsPage

class VolumePage(BarLevelPage):
    async def __init__(self):
        await super().__init__(
            title="Volume",
            level=CONFIG.get('volume', 1.0),
        )

    def set_level(self, level: float):
        if super().set_level(level):
            self.manager.player.volume = level
            return True

    async def right_pressed(self):
        return 'Settings'
