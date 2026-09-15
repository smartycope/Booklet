from typing import Any
from src import THEME
from src.pages.Page import Page
from src.aobject import aobject


class ListPage(Page, aobject):
    async def __init__(self, items: list[str] | dict[str, Any], scrollable, title='', vspacing=6, **kwargs):
        super().__init__(**kwargs)
        self.item_map = items if isinstance(items, dict) else {k: k for k in items}
        self.items = list(items)
        self.scrollable = scrollable
        self.title = title
        self.selected_index = 0
        self._text_height = self.draw.textbbox((0, 0), 'A', THEME['font'])[1]
        self.vspacing = vspacing
        self._draw_items()

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
        text_width = self.draw.textlength(self.title, THEME['font'])

        bbox = self.text(self.title, (self.width - text_width) / 2, 2)
        self.draw.line((2, bbox[3]+2, self.width-2, bbox[3]+2), fill=THEME["text_color"], width=3)

        for i, item in enumerate(self.items):
            y = self._item_y(i)
            if i == self.selected_index:
                text_bbox = self.draw.textbbox((2, y), item, font=THEME['font'])
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
                bbox = self.text(item, 2, y, inverted=True)
            else:
                bbox = self.text(item, 2, y)

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
