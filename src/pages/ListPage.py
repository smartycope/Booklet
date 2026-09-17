from collections.abc import Sequence
from typing import Any
from src import THEME
from src.pages.Page import Page
from src.aobject import aobject
from src import font

# TODO: if the text of a single item is longer than the screen width, marquee it

class ListPage(Page, aobject):
    async def __init__(
        self,
        items: list[str] | dict[str, Any] | Sequence[tuple[str, Any]],
        scrollable,
        title='',
        vspacing=6,
        text_size=THEME["text_size"],
        empty_text="No items",
    ):
        super().__init__()
        if isinstance(items, dict):
            self.entries = list(items.items())
        else:
            self.entries = [
                (item[0], item[1]) if isinstance(item, tuple) and len(item) == 2 else (item, item)
                for item in items
            ]
        self.item_map = dict(self.entries)
        self.items = [label for label, _value in self.entries]
        self.scrollable = scrollable
        self._title = title
        self.empty_text = empty_text
        self.selected_index = 0
        self.font = font(text_size)
        text_bbox = self.draw.textbbox((0, 0), 'Ag', font=self.font)
        self._text_height = text_bbox[3] - text_bbox[1]
        self.vspacing = vspacing
        self._instantiated = True
        self._draw_items()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        # If we try to set the title before the page is instantiated, that's fine
        try:
            if self._instantiated:
                self._draw_items()
        except AttributeError:
            pass

    @property
    def selected_item(self):
        return self.items[self.selected_index] if self.items else None

    @property
    def selected_value(self):
        return self.entries[self.selected_index][1] if self.entries else None

    @selected_item.setter
    def selected_item(self, value):
        self.selected_index = self.items.index(value)

    def _item_y(self, index):
        # +1 + vspacing for the title
        return (index + 1) * ((self.vspacing * 2) + self._text_height) + (self.vspacing * 2)

    def _draw_items(self):
        self.reset_img()
        text_width = self.draw.textlength(self.title, self.font)

        bbox = self.text(self.title, (self.width - text_width) / 2, 2, font=self.font)
        self.draw.line((2, bbox[3]+2, self.width-2, bbox[3]+2), fill=THEME["text_color"], width=3)

        if not self.items:
            self.text(self.empty_text, 2, self._item_y(0), font=self.font)
            return

        visible_count = len(self.items)
        if self.scrollable:
            visible_count = 0
            while visible_count < len(self.items):
                bbox = self.draw.textbbox(
                    (2, self._item_y(visible_count)),
                    self.items[visible_count],
                    font=self.font,
                )
                if bbox[3] + self.vspacing > self.height:
                    break
                visible_count += 1
            visible_count = max(1, visible_count)

        first_index = 0
        if self.scrollable and self.selected_index >= visible_count:
            first_index = self.selected_index - visible_count + 1

        last_index = min(len(self.items), first_index + visible_count)
        for row, i in enumerate(range(first_index, last_index)):
            item = self.items[i]
            y = self._item_y(row)
            if i == self.selected_index:
                text_bbox = self.draw.textbbox((2, y), item, font=self.font)
                padding = self.vspacing // 2
                self.draw.rounded_rectangle(
                    (
                        0,
                        text_bbox[1] - padding,
                        self.width - 1,
                        text_bbox[3] + padding,
                    ),
                    fill=THEME["text_color"],
                    radius=THEME['radius']
                )
                bbox = self.text(item, 2, y, inverted=True, font=self.font)
            else:
                bbox = self.text(item, 2, y, font=self.font)

    # TODO: these could be optimized
    async def down_pressed(self):
        if not self.items:
            return None
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self._draw_items()
        return True

    async def up_pressed(self):
        if not self.items:
            return None
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self._draw_items()
        return True

    async def center_pressed(self):
        if not self.items:
            return None
        result = self.item_selected(self.selected_value)
        if hasattr(result, "__await__"):
            return await result
        return result

    def item_selected(self, item):
        pass
