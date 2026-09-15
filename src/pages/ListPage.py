from typing import Any
from PIL import ImageFont
from src import ASSETS, THEME
from src.pages.Page import Page
from src.aobject import aobject
from src import font


class ListPage(Page, aobject):
    async def __init__(self, items: list[str] | dict[str, Any], scrollable, title='', vspacing=6, text_size=THEME["text_size"]):
        super().__init__()
        self.item_map = items if isinstance(items, dict) else {k: k for k in items}
        self.items = list(items)
        self.scrollable = scrollable
        self._title = title
        self.selected_index = 0
        self.font = font(text_size)
        self._text_height = self.draw.textbbox((0, 0), 'A', self.font)[1]
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
        return self.items[self.selected_index]

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

        last_index = first_index + visible_count
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
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self._draw_items()
        return True

    async def up_pressed(self):
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self._draw_items()
        return True

    async def center_pressed(self):
        return self.item_selected(self.item_map[self.selected_item])

    def item_selected(self, item):
        pass
