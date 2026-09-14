from src.pages.BarLevelPage import BarLevelPage


class VolumePage(BarLevelPage):
    def __init__(self):
        super().__init__(
            title="Volume",
            level=0.5,
            right_pressed="settings",
        )

    def set_level(self, level: float):
        if super().set_level(level):
            print(f"Volume set to {level}")
