from collections.abc import Callable

from src.constants import THEME
from src.pages.Page import Page


class BarLevelPage(Page):
    """A page for displaying and changing a normalized value as a bar."""

    def __init__(
        self,
        title: str,
        level: float = 0.5,
        step: float = 0.1,
        on_change: Callable[[float], None] | None = None,
        **kwargs,
    ):
        if step <= 0:
            raise ValueError("step must be greater than zero")

        self.title = title
        self.step = step
        self.on_change = on_change
        self._level = self._clamp(level)
        super().__init__(**kwargs)
        self._draw_page()

    @staticmethod
    def _clamp(level: float) -> float:
        return max(0.0, min(1.0, float(level)))

    @property
    def level(self) -> float:
        return self._level

    def set_level(self, level: float) -> bool:
        """Set the level and return whether the displayed value changed."""
        new_level = self._clamp(level)
        if new_level == self._level:
            return False

        self._level = new_level
        if self.on_change is not None:
            self.on_change(new_level)
        self._draw_page()
        return True

    def _draw_page(self) -> None:
        self.reset_img()

        title_width = self.draw.textlength(self.title, font=THEME["font"])
        title_bbox = self.text(self.title, (self.width - title_width) / 2, 2)
        self.draw.line(
            (2, title_bbox[3] + 2, self.width - 2, title_bbox[3] + 2),
            fill=THEME["text_color"],
            width=3,
        )

        bar_left = (self.width - 28) // 2
        bar_top = title_bbox[3] + 20
        bar_right = bar_left + 28
        bar_bottom = self.height - 50
        self.draw.rounded_rectangle(
            (bar_left, bar_top, bar_right, bar_bottom),
            outline=THEME["text_color"],
            width=3,
            radius=THEME["radius"],
        )

        fill_height = max(0, bar_bottom - bar_top - 6)
        fill_amount = round(fill_height * self.level)
        fill_top = bar_bottom - 3 - fill_amount
        if fill_top < bar_top + 3:
            fill_top = bar_top + 3
        if fill_top < bar_bottom - 3:
            self.draw.rectangle(
                (bar_left + 3, fill_top, bar_right - 3, bar_bottom - 3),
                fill=THEME["text_color"],
            )

        percentage = f"{round(self.level * 100)}%"
        percentage_width = self.draw.textlength(percentage, font=THEME["font"])
        self.text(
            percentage,
            (self.width - percentage_width) / 2,
            bar_bottom + 12,
        )

    def up_pressed(self):
        return self.set_level(self.level + self.step)

    def down_pressed(self):
        return self.set_level(self.level - self.step)

    def up_held(self):
        return self.up_pressed()

    def down_held(self):
        return self.down_pressed()
