import asyncio
from collections import deque
import time

from src import THEME
from src.DownloadStore import DownloadStore
from src.aobject import aobject
from src.pages.Page import Page


class DownloadBookPage(Page, aobject):
    async def __init__(self, book_id: str, back_route="AudiobookshelfLanding"):
        super().__init__()
        self.book_id = book_id
        self.back_route = back_route
        self.book = await self.manager.api.get_book(book_id)
        self.store = DownloadStore()
        self.active = False
        self.complete = False
        self.error = None
        self.downloaded = 0
        self.total = self.book.size or None
        self._task = None
        self._progress_samples = deque(maxlen=20)
        self._draw()

    async def on_enter(self):
        if self.store.contains(self.book_id):
            self.complete = True
            self._draw("Already downloaded")
            self.manager.render()
            return
        self.active = True
        self._progress_samples.clear()
        self._progress_samples.append((time.monotonic(), 0))
        self._draw("Starting download\nHold center to cancel")
        self.manager.render()
        self._task = asyncio.create_task(self._download())

    async def _download(self):
        try:
            await self.store.download(self.manager.api, self.book, self._progress)
            self.complete = True
        except asyncio.CancelledError:
            raise
        except Exception as error:
            self.error = error
        finally:
            self.active = False
            self._draw()
            if self.manager.current_page is self:
                self.manager.render()

    def _progress(self, downloaded: int, _response_total: int | None):
        self.downloaded = downloaded
        self._progress_samples.append((time.monotonic(), downloaded))
        self._draw()
        if self.manager.current_page is self:
            self.manager.render()

    @staticmethod
    def _format_size(size: int) -> str:
        value = float(size)
        units = ("bytes", "KB", "MB", "GB", "TB")
        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == "bytes":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024

    @staticmethod
    def _format_duration(seconds: float) -> str:
        seconds = max(0, round(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}h {minutes}m"
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _estimated_seconds_remaining(self):
        if not self.total or len(self._progress_samples) < 2:
            return None
        first_time, first_bytes = self._progress_samples[0]
        last_time, last_bytes = self._progress_samples[-1]
        elapsed = last_time - first_time
        transferred = last_bytes - first_bytes
        if elapsed < 0.5 or transferred <= 0:
            return None
        bytes_per_second = transferred / elapsed
        return max(0.0, self.total - self.downloaded) / bytes_per_second

    def _draw(self, status=None):
        self.reset_img()
        title = "Downloading"
        width = self.draw.textlength(title, font=THEME["font"])
        self.text(title, (self.width - width) / 2, 3)
        self.draw.line((2, 24, self.width - 2, 24), fill=THEME["text_color"], width=3)
        book_title = self.book.title
        if self.draw.textlength(book_title, font=THEME["font"]) > self.width - 8:
            while book_title and self.draw.textlength(book_title + "…", font=THEME["font"]) > self.width - 8:
                book_title = book_title[:-1]
            book_title += "…"
        self.text(book_title, 4, 38)

        if self.error:
            status = f"Failed: {self.error}"
        elif self.complete:
            status = status or "Download complete\nLeft to return"
        elif self.total:
            estimate = self._estimated_seconds_remaining()
            estimate_line = (
                f"ETA: {self._format_duration(estimate)}\n"
                if estimate is not None else ""
            )
            status = (
                f"{self._format_size(self.downloaded)} / {self._format_size(self.total)}\n"
                f"{min(100, round(self.downloaded * 100 / self.total))}%\n"
                f"{estimate_line}"
                "Hold center to cancel"
            )
        else:
            status = status or f"{self._format_size(self.downloaded)}\nHold center to cancel"

        if self.total:
            bar = (10, 96, self.width - 10, 123)
            self.draw.rounded_rectangle(bar, outline=THEME["text_color"], width=2, radius=THEME["radius"])
            fraction = min(1.0, self.downloaded / self.total)
            fill_right = 13 + round((self.width - 26) * fraction)
            if fill_right > 13:
                self.draw.rectangle((13, 99, fill_right, 120), fill=THEME["text_color"])
        for index, line in enumerate(str(status).split("\n")):
            self.text(line, 5, 137 + index * 24, font=self.manager.small_font)

    async def left_pressed(self):
        if not self.active:
            return self.back_route

    async def center_held(self):
        if self.active and self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            return self.back_route

    async def on_exit(self):
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
