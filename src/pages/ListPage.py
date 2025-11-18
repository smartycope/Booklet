from abc import abstractmethod
from typing import Callable, Any
from src.constants import THEME
from src.pages.Page import Page

class ListPage(Page):
    def __init__(self, items: list[str] | dict[str, Any], scrollable, title='', vspacing=6, **kwargs):
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
                # TODO: this needs work, it's close enough for now
                self.draw.rounded_rectangle(
                    (0, y+(self.vspacing//2), self.width, y + self._text_height + (self.vspacing*2)),
                    fill=THEME["text_color"],
                    radius=THEME['radius']
                )
                bbox = self.text(item, 2, y, inverted=True)
            else:
                bbox = self.text(item, 2, y)

    # TODO: these could be optimized
    def down_pressed(self):
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self._draw_items()
        return True

    def up_pressed(self):
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self._draw_items()
        return True

    def center_pressed(self):
        return self.item_selected(self.item_map[self.selected_item])

    def item_selected(self, item):
        pass