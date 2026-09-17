import asyncio
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from src import CONFIG, THEME
from src.pages.ListPage import ListPage


class SettingsPage(ListPage):
    speed_min = 0.5
    speed_max = 4.0
    timeout_options = (10, 30, 60, 120, 300, 600)
    bar_dark = THEME["text_color"]
    bar_light = THEME["bg"]

    async def __init__(self):
        self.update_status = ""
        CONFIG.setdefault("volume", 1.0)
        CONFIG.setdefault("brightness", 1.0)
        CONFIG.setdefault("default_playback_speed", 1.0)
        CONFIG.setdefault("screensaver_timeout", 30)
        await super().__init__(
            items=[
                ("Bluetooth", "Bluetooth"),
                ("Brightness", "brightness"),
                ("Volume", "volume"),
                ("Default playback speed", "default_playback_speed"),
                ("Screensaver timeout", "screensaver_timeout"),
                ("Check for updates", "check_for_updates"),
                ("Reboot", "reboot"),
                ("Low power mode (press left to wake)", "low_power_mode"),
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

        if self.update_status:
            status = self.update_status
            while status and self.draw.textlength(status + "…", font=self.manager.small_font) > self.width - 8:
                status = status[:-1]
            if status != self.update_status:
                status += "…"
            self.text(status, 4, self.height - 18, font=self.manager.small_font)

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

    async def check_for_updates(self):
            self.update_status = "Checking for updates…"
            self._draw_items()
            self.manager.render()
            try:
                process = await asyncio.create_subprocess_exec(
                    "git", "pull",
                    cwd=Path.cwd(),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
                output, _unused = await process.communicate()
                lines = [line.strip() for line in output.decode(errors="replace").splitlines() if line.strip()]
                if process.returncode == 0:
                    self.update_status = lines[-1] if lines else "Update complete"
                else:
                    self.update_status = f"Update failed ({process.returncode})"
            except (OSError, subprocess.SubprocessError) as error:
                self.update_status = f"Update failed: {error}"
            self._draw_items()
            self.manager.render()
            return True

    async def reboot(self):
        self.update_status = "Rebooting…"
        self._draw_items()
        self.manager.render()
        try:
            process = await asyncio.create_subprocess_exec(
                "reboot",
                cwd=Path.cwd(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            output, _unused = await process.communicate()
            lines = [line.strip() for line in output.decode(errors="replace").splitlines() if line.strip()]
            if process.returncode != 0:
                self.update_status = f"Failed to reboot ({process.returncode})"
        except (OSError, subprocess.SubprocessError) as error:
            self.update_status = f"Reboot failed: {error}"
        self._draw_items()
        self.manager.render()
        # Do we need to manually exit here?
        # await self.manager.shutdown()
        return True

    async def low_power_mode(self):
        self.update_status = "Shutting Down…"
        self._draw_items()
        self.manager.render()
        try:
            process = await asyncio.create_subprocess_exec(
                "halt",
                cwd=Path.cwd(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            output, _unused = await process.communicate()
            lines = [line.strip() for line in output.decode(errors="replace").splitlines() if line.strip()]
            if process.returncode != 0:
                self.update_status = f"Failed to halt ({process.returncode})"
        except (OSError, subprocess.SubprocessError) as error:
            self.update_status = f"Halt failed: {error}"
        self._draw_items()
        self.manager.render()
        # Do we need to manually exit here?
        # await self.manager.shutdown()
        return True

    async def left_pressed(self):
        return self._change_setting(-1)

    async def right_pressed(self):
        return self._change_setting(1)

    async def center_pressed(self):
        if self.selected_value == "check_for_updates":
            return await self.check_for_updates()
        if self.selected_value == "reboot":
            return await self.reboot()
        if self.selected_value == "low_power_mode":
            return await self.low_power_mode()
        if self.selected_value in {"Bluetooth", "Landing"}:
            return self.selected_value

    async def key2_pressed(self):
        return "Landing"
