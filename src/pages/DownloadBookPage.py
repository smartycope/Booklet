import asyncio

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
        self.total = None
        self._task = None
        self._draw()

    async def on_enter(self):
        if self.store.contains(self.book_id):
            self.complete = True
            self._draw("Already downloaded")
            self.manager.render()
            return
        self.active = True
        self._draw("Starting download")
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

    def _progress(self, downloaded: int, total: int | None):
        self.downloaded, self.total = downloaded, total
        self._draw()
        if self.manager.current_page is self:
            self.manager.render()

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
            status = f"{round(self.downloaded * 100 / self.total)}%"
        else:
            status = status or f"{self.downloaded // 1024} KiB"

        bar = (10, 105, self.width - 10, 132)
        self.draw.rounded_rectangle(bar, outline=THEME["text_color"], width=2, radius=THEME["radius"])
        if self.total and self.downloaded:
            fraction = min(1.0, self.downloaded / self.total)
            self.draw.rectangle((13, 108, 13 + round((self.width - 26) * fraction), 129), fill=THEME["text_color"])
        for index, line in enumerate(str(status).split("\n")):
            self.text(line, 5, 150 + index * 24)

    async def left_pressed(self):
        if not self.active:
            return self.back_route

    async def on_exit(self):
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
