import asyncio
import time
from collections.abc import Sequence
from typing import Any

from src import THEME, font
from src.aobject import aobject
from src.pages.Page import Page


class ListPage(Page, aobject):
    marquee_delay = 1.25
    marquee_speed = 28
    marquee_refresh_interval = 0.1

    async def __init__(
        self,
        items: list[str] | dict[str, Any] | Sequence[tuple[str, Any]],
        scrollable,
        title='',
        vspacing=4,
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
        self._first_visible_index = 0
        self._selection_changed_at = time.monotonic()
        self._marquee_task = None
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
        self._select_index(self.items.index(value))

    def _item_y(self, index):
        return (index + 1) * ((self.vspacing * 2) + self._text_height) + (self.vspacing * 2)

    def _visible_count(self):
        if not self.scrollable:
            return len(self.items)
        count = 0
        while count < len(self.items):
            bbox = self.draw.textbbox((2, self._item_y(count)), self.items[count], font=self.font)
            if bbox[3] + self.vspacing > self.height:
                break
            count += 1
        return max(1, count)

    def _select_index(self, index: int, *, wrap=False):
        if not self.items:
            return False
        old_index = self.selected_index
        index = index % len(self.items) if wrap else min(max(0, index), len(self.items) - 1)
        self.selected_index = index

        visible_count = self._visible_count()
        max_first = max(0, len(self.items) - visible_count)
        if index < self._first_visible_index:
            self._first_visible_index = index
        elif index >= self._first_visible_index + visible_count:
            self._first_visible_index = index - visible_count + 1
        self._first_visible_index = min(max(0, self._first_visible_index), max_first)
        if index != old_index:
            self._selection_changed_at = time.monotonic()
        self._draw_items()
        return index != old_index

    def move_selection(self, amount: int, *, wrap=False):
        return self._select_index(self.selected_index + amount, wrap=wrap)

    def _marquee_offset(self, item: str, available_width: int) -> int:
        overflow = max(0, round(self.draw.textlength(item, font=self.font) - available_width))
        if overflow == 0:
            return 0
        elapsed = time.monotonic() - self._selection_changed_at
        travel_time = overflow / self.marquee_speed
        cycle = (2 * self.marquee_delay) + (2 * travel_time)
        phase = elapsed % cycle
        if phase <= self.marquee_delay:
            return 0
        phase -= self.marquee_delay
        if phase <= travel_time:
            return round(phase * self.marquee_speed)
        phase -= travel_time
        if phase <= self.marquee_delay:
            return overflow
        phase -= self.marquee_delay
        return max(0, overflow - round(phase * self.marquee_speed))

    def _draw_scrollbar(self, visible_count: int):
        if not self.scrollable or len(self.items) <= visible_count:
            return
        top = self._item_y(0) - self.vspacing // 2
        bottom = self.height - 3
        track_height = bottom - top
        x = self.width - 3
        # Clear text beneath the narrow scrollbar gutter.
        self.draw.rectangle((self.width - 6, top, self.width - 1, bottom), fill=THEME["bg"])
        self.draw.line((x, top, x, bottom), fill=THEME["text_color"], width=1)
        thumb_height = max(8, round(track_height * visible_count / len(self.items)))
        max_first = len(self.items) - visible_count
        thumb_top = top + round((track_height - thumb_height) * self._first_visible_index / max_first)
        self.draw.line((x, thumb_top, x, thumb_top + thumb_height), fill=THEME["text_color"], width=3)

    def _draw_items(self):
        self.reset_img()
        text_width = self.draw.textlength(self.title, self.font)
        bbox = self.text(self.title, (self.width - text_width) / 2, 2, font=self.font)
        self.draw.line((2, bbox[3] + 2, self.width - 2, bbox[3] + 2), fill=THEME["text_color"], width=3)

        if not self.items:
            self.text(self.empty_text, 2, self._item_y(0), font=self.font)
            return

        visible_count = self._visible_count()
        max_first = max(0, len(self.items) - visible_count)
        self._first_visible_index = min(max(0, self._first_visible_index), max_first)
        last_index = min(len(self.items), self._first_visible_index + visible_count)
        has_scrollbar = self.scrollable and len(self.items) > visible_count
        available_width = self.width - (10 if has_scrollbar else 4)

        for row, i in enumerate(range(self._first_visible_index, last_index)):
            item = self.items[i]
            y = self._item_y(row)
            if i == self.selected_index:
                text_bbox = self.draw.textbbox((2, y), item, font=self.font)
                padding = self.vspacing // 2
                self.draw.rounded_rectangle(
                    (0, text_bbox[1] - padding, self.width - 1, text_bbox[3] + padding),
                    fill=THEME["text_color"], radius=THEME['radius'],
                )
                offset = self._marquee_offset(item, available_width)
                self.text(item, 2 - offset, y, inverted=True, font=self.font)
            else:
                self.text(item, 2, y, font=self.font)
        self._draw_scrollbar(visible_count)

    async def on_enter(self):
        if self._marquee_task is None or self._marquee_task.done():
            self._marquee_task = asyncio.create_task(self._marquee_loop())

    async def on_exit(self):
        if self._marquee_task and not self._marquee_task.done():
            self._marquee_task.cancel()
            try:
                await self._marquee_task
            except asyncio.CancelledError:
                pass

    async def _marquee_loop(self):
        while True:
            await asyncio.sleep(self.marquee_refresh_interval)
            if not self.items:
                continue
            visible_count = self._visible_count()
            available = self.width - (10 if len(self.items) > visible_count else 4)
            if self.draw.textlength(self.selected_item, font=self.font) <= available:
                continue
            self._draw_items()
            if self.manager.current_page is self:
                self.manager.render()

    async def down_pressed(self):
        if not self.items:
            return None
        self.move_selection(1, wrap=True)
        return True

    async def up_pressed(self):
        if not self.items:
            return None
        self.move_selection(-1, wrap=True)
        return True

    async def down_held(self):
        return await self.down_pressed()

    async def up_held(self):
        return await self.up_pressed()

    async def center_pressed(self):
        if not self.items:
            return None
        result = self.item_selected(self.selected_value)
        if hasattr(result, "__await__"):
            return await result
        return result

    async def key1_pressed(self):
        self.move_selection(-10)
        return True

    async def key3_pressed(self):
        self.move_selection(10)
        return True

    async def key1_held(self):
        # Jump to the top
        self._first_visible_index = 0
        return True

    async def key3_held(self):
        # Jump to the bottom
        self._first_visible_index = max(0, len(self.items) - self._visible_count())
        return True

    def item_selected(self, item):
        pass
