from PIL import Image, ImageDraw

from src import CONFIG, THEME
from src.pages.ListPage import ListPage


class SettingsPage(ListPage):
    speed_min = 0.5
    speed_max = 4.0
    timeout_options = (10, 30, 60, 120, 300, 600)
    bar_dark = "#3D2C24"
    bar_light = "#FFEFD7"

    async def __init__(self):
        CONFIG.setdefault("volume", 1.0)
        CONFIG.setdefault("brightness", 1.0)
        CONFIG.setdefault("default_playback_speed", 1.0)
        CONFIG.setdefault("screensaver_timeout", 30)
        await super().__init__(
            items=[
                ("Brightness", "brightness"),
                ("Volume", "volume"),
                ("Default playback speed", "default_playback_speed"),
                ("Screensaver timeout", "screensaver_timeout"),
                ("Bluetooth", "Bluetooth"),
                ("Back", "Landing"),
            ],
            scrollable=False,
            title="Settings",
            text_size=13,
            vspacing=4,
        )

    def _setting_level(self, key):
        if key in {"brightness", "volume"}:
            return max(0.01, min(1.0, float(CONFIG.get(key, 1.0))))
        if key == "default_playback_speed":
            speed = float(CONFIG.get(key, 1.0))
            return (speed - self.speed_min) / (self.speed_max - self.speed_min)
        if key == "screensaver_timeout":
            value = int(CONFIG.get(key, 30))
            index = min(
                range(len(self.timeout_options)),
                key=lambda candidate: abs(self.timeout_options[candidate] - value),
            )
            return index / (len(self.timeout_options) - 1)
        return None

    def _display_label(self, key, fallback):
        if key == "screensaver_timeout":
            return f"Screensaver: {int(CONFIG.get(key, 30))}s"
        if key == "default_playback_speed":
            return f"Default speed: {float(CONFIG.get(key, 1.0)):.1f}x"
        return fallback

    def _draw_items(self):
        self.reset_img()
        title_width = self.draw.textlength(self.title, font=self.font)
        bbox = self.text(self.title, (self.width - title_width) / 2, 2, font=self.font)
        self.draw.line(
            (2, bbox[3] + 2, self.width - 2, bbox[3] + 2),
            fill=THEME["text_color"], width=3,
        )

        for row, (fallback, key) in enumerate(self.entries):
            label = self._display_label(key, fallback)
            y = self._item_y(row)
            text_bbox = self.draw.textbbox((4, y), label, font=self.font)
            padding = self.vspacing
            top = text_bbox[1] - padding
            bottom = text_bbox[3] + padding
            level = self._setting_level(key)

            if level is not None:
                split = round(self.width * max(0.0, min(1.0, level)))
                self.draw.rectangle((0, top, self.width - 1, bottom), fill=self.bar_light)
                if split > 0:
                    self.draw.rectangle((0, top, split, bottom), fill=self.bar_light)
                self.text(label, 4, y + 2, font=self.font, fill=self.bar_dark)
                if split > 0:
                    left = Image.new("RGB", (split, bottom - top + 1 - 2), self.bar_dark)
                    left_draw = ImageDraw.Draw(left)
                    left_draw.text((4, y - top), label, font=self.font, fill=self.bar_light)
                    self.img.paste(left, (2, top + 2))
                    self.draw = ImageDraw.Draw(self.img)
            else:
                self.text(label, 4, y, font=self.font)

            if row == self.selected_index:
                split = round(self.width * (level or 0)) if level is not None else 0
                if level is None:
                    self.draw.rectangle(
                        (1, top, self.width - 2, bottom),
                        outline=THEME["text_color"], width=2,
                    )
                elif split >= self.width:
                    self.draw.rectangle(
                        (1, top, self.width - 2, bottom),
                        outline=self.bar_light, width=2,
                    )
                elif split <= 0:
                    self.draw.rectangle(
                        (1, top, self.width - 2, bottom),
                        outline=self.bar_dark, width=2,
                    )
                else:
                    # Invert each outline segment over its background half.
                    self.draw.line((1, top, split, top), fill=self.bar_light, width=2)
                    self.draw.line((1, bottom, split, bottom), fill=self.bar_light, width=2)
                    self.draw.line((1, top, 1, bottom), fill=self.bar_light, width=2)
                    self.draw.line((split, top, self.width - 2, top), fill=self.bar_dark, width=2)
                    self.draw.line((split, bottom, self.width - 2, bottom), fill=self.bar_dark, width=2)
                    self.draw.line((self.width - 2, top, self.width - 2, bottom), fill=self.bar_dark, width=2)

    def _change_setting(self, direction):
        key = self.selected_value
        if key == "brightness":
            value = max(0.0, min(1.0, round(float(CONFIG.get(key, 1.0)) + direction * 0.1, 1)))
            self.manager.screen.brightness = value
        elif key == "volume":
            value = max(0.0, min(1.0, round(float(CONFIG.get(key, 1.0)) + direction * 0.1, 1)))
            CONFIG[key] = value
            self.manager.player.volume = value
        elif key == "default_playback_speed":
            value = max(
                self.speed_min,
                min(self.speed_max, round(float(CONFIG.get(key, 1.0)) + direction * 0.1, 1)),
            )
            CONFIG[key] = value
        elif key == "screensaver_timeout":
            current = int(CONFIG.get(key, 30))
            index = min(
                range(len(self.timeout_options)),
                key=lambda candidate: abs(self.timeout_options[candidate] - current),
            )
            index = max(0, min(len(self.timeout_options) - 1, index + direction))
            CONFIG[key] = self.timeout_options[index]
        else:
            return False
        CONFIG.sync()
        self._draw_items()
        return True

    async def left_pressed(self):
        return self._change_setting(-1)

    async def right_pressed(self):
        return self._change_setting(1)

    async def center_pressed(self):
        if self.selected_value in {"Bluetooth", "Landing"}:
            return self.selected_value

    async def key2_pressed(self):
        return "Landing"
