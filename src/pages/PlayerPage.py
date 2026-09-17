import asyncio

from src import THEME
from src.aobject import aobject
from src.pages.Page import Page


def format_time(seconds: float) -> str:
    seconds = max(0, round(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"


class PlayerPage(Page, aobject):
    sync_interval = 15

    async def __init__(self, book_id: str, local=False, back_route="AudiobookshelfLanding"):
        super().__init__()
        self.book_id = book_id
        self.local = local
        self.back_route = back_route
        self._task = None
        # If false, up and down change the playback speed instead of the volume
        self.volume_mode = True
        # TODO: There should be some way to dynamically get this, but this works for now
        self.small_font_height = 11
        await self.manager.activate_book(book_id, local, back_route)
        self._draw()

    async def on_enter(self):
        self._task = asyncio.create_task(self._refresh_loop())

    async def on_exit(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.manager.pause_active_playback()

    async def _refresh_loop(self):
        ticks = 0
        while True:
            await asyncio.sleep(1)
            ticks += 1
            self.manager.player.poll()
            self._draw()
            if self.manager.current_page is self:
                self.manager.render()
            if ticks % self.sync_interval == 0:
                await self.manager.sync_active_playback(suppress_errors=True)

    def _fit(self, text: str, width: int | None = None) -> str:
        width = width or self.width - 8
        if self.draw.textlength(text, font=THEME["font"]) <= width:
            return text
        text = text.rstrip()
        while text and self.draw.textlength(text + "…", font=THEME["font"]) > width:
            text = text[:-1]
        return text + "…"

    def _draw(self):
        self.reset_img()
        context = self.manager.active_playback
        if context is None:
            self.text("No audiobook loaded", 4, 4)
            return
        player = self.manager.player
        self.text(self._fit(context.book.title), 4, 4)
        author = ", ".join(context.book.authors)
        if author:
            self.text(self._fit(author), 4, 30, font=self.manager.small_font)
        self.draw.line((2, 52, self.width - 2, 52), fill=THEME["text_color"], width=2)

        chapter = player.current_chapter
        chapter_title = chapter.title if chapter else "No chapter information"
        self.text(self._fit(chapter_title), 4, 68, font=self.manager.small_font)

        position, duration = player.position, context.book.duration or player.duration
        self.text(f"{format_time(position)} / {format_time(duration)}", 4, 101)
        bar = (10, 132, self.width - 10, 154)
        self.draw.rounded_rectangle(bar, outline=THEME["text_color"], width=2, radius=THEME["radius"])
        if duration > 0:
            fraction = min(1.0, position / duration)
            self.draw.rectangle((13, 135, 13 + round((self.width - 26) * fraction), 151), fill=THEME["text_color"])
        self.text(player.state, 4, 172)
        # self.text("1/3 chapter  Hold: back", 4, 205, font=self.manager.small_font)
        volume_text_width = self.draw.textlength("Volume: 100%", font=self.manager.small_font)
        spacer_width = self.draw.textlength(" | ", font=self.manager.small_font)
        speed_text_width = self.draw.textlength("Speed: 1.0", font=self.manager.small_font)
        self.text(f"Volume: {player.volume * 100:.0f}% | Speed: {player.rate:.1f}", 4, 205, font=self.manager.small_font)
        # Underline the appropriate mode
        y = 205 + self.small_font_height + 2
        if self.volume_mode:
            self.draw.line((4, y, 4 + volume_text_width, y), fill=THEME["text_color"], width=2)
        else:
            self.draw.line((4 + volume_text_width + spacer_width, y, 4 + volume_text_width + spacer_width + speed_text_width, y), fill=THEME["text_color"], width=2)

    # Toggle volume/speed mode
    async def center_pressed(self):
        self.volume_mode = not self.volume_mode
        self._draw()
        return True

    # Exit player
    async def center_held(self):
        self.manager.player.pause()
        await self.manager.sync_active_playback(suppress_errors=True)
        return self.back_route

    # Seek backward
    async def left_pressed(self):
        self.manager.player.seek_relative(-30)
        await self.manager.sync_active_playback(suppress_errors=True)
        self._draw()
        return True

    # Seek forward
    async def right_pressed(self):
        self.manager.player.seek_relative(30)
        await self.manager.sync_active_playback(suppress_errors=True)
        self._draw()
        return True

    # Volume up/Increase playback speed
    async def up_pressed(self):
        if self.volume_mode:
            self.manager.player.volume_up()
        else:
            self.manager.player.rate_up()
        self._draw()
        return True

    # Volume down/Decrease playback speed
    async def down_pressed(self):
        if self.volume_mode:
            self.manager.player.volume_down()
        else:
            self.manager.player.rate_down()
        self._draw()
        return True

    # Play/Pause
    async def key2_pressed(self):
        self.manager.player.play_pause()
        await self.manager.sync_active_playback(suppress_errors=True)
        self._draw()
        return True

    # TODO: add bookmark
    async def key2_held(self):
        pass

    # Previous chapter
    async def key1_pressed(self):
        self.manager.player.previous_chapter()
        await self.manager.sync_active_playback(suppress_errors=True)
        self._draw()
        return True

    # Next chapter
    async def key3_pressed(self):
        self.manager.player.next_chapter()
        await self.manager.sync_active_playback(suppress_errors=True)
        self._draw()
        return True
