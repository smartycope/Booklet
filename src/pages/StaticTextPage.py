from PIL import ImageFont

from src import ASSETS, THEME
from src.pages.Page import Page


class StaticTextPage(Page):
    """ A page of wrapped, vertically scrollable text.
        NOT an aobject, so the ErrorPage can be called syncronously.
        When inheriting, be sure to also inherit aobject.
    """

    def __init__(self, text, text_size=THEME["text_size"]):
        super().__init__()
        self.content = str(text)
        self.text_size = text_size
        self.font = ImageFont.truetype(
            str(ASSETS / "Orbitron-VariableFont_wght.ttf"),
            size=text_size,
        )
        self.margin = 5
        self.line_height = max(
            1,
            self.draw.textbbox((0, 0), "Ag", font=self.font)[3],
        )
        self.visible_line_count = max(
            1,
            (self.height - (2 * self.margin)) // self.line_height,
        )
        self.lines = self._wrap_text(self.content)
        self.scroll_offset = 0
        self._draw_text()

    def _wrap_text(self, text):
        """Wrap each newline-delimited paragraph to the available pixel width."""
        max_width = self.width - (2 * self.margin)
        lines = []

        for paragraph in text.split("\n"):
            if not paragraph:
                lines.append("")
                continue

            line = ""
            for word in paragraph.split():
                candidate = f"{line} {word}" if line else word
                if self.draw.textlength(candidate, font=self.font) <= max_width:
                    line = candidate
                    continue

                if line:
                    lines.append(line)
                    line = ""

                # Split a single word when it is wider than the screen.
                for character in word:
                    candidate = line + character
                    if line and self.draw.textlength(candidate, font=self.font) > max_width:
                        lines.append(line)
                        line = character
                    else:
                        line = candidate

            lines.append(line)

        return lines

    @property
    def max_scroll_offset(self):
        return max(0, len(self.lines) - self.visible_line_count)

    def _draw_text(self):
        self.reset_img()
        visible_lines = self.lines[
            self.scroll_offset:self.scroll_offset + self.visible_line_count
        ]
        for index, line in enumerate(visible_lines):
            self.draw.text(
                (self.margin, self.margin + (index * self.line_height)),
                line,
                font=self.font,
                fill=THEME["text_color"],
            )

    async def down_pressed(self):
        if self.scroll_offset >= self.max_scroll_offset:
            return None
        self.scroll_offset += 1
        self._draw_text()
        return True

    async def up_pressed(self):
        if self.scroll_offset == 0:
            return None
        self.scroll_offset -= 1
        self._draw_text()
        return True
