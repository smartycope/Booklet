from src import CONFIG
from src.DownloadStore import DownloadStore
from src.aobject import aobject
from src.pages.ListPage import ListPage
from src.pages.StaticTextPage import StaticTextPage


class SelectDownloadedBookPage(ListPage):
    async def __init__(self, delete=False):
        self.delete = delete
        self.store = DownloadStore()
        books = self.store.list_books()
        route = ("SelectDownloadedBook", {"delete": delete})
        items = []
        for book in books:
            if delete:
                destination = (
                    "DeleteDownloadedBook",
                    {"book_id": book.id, "title": book.title, "back_route": route},
                )
            else:
                destination = (
                    "Player",
                    {"book_id": book.id, "local": True, "back_route": route},
                )
            items.append((book.title, destination))
        await super().__init__(
            items=items,
            scrollable=True,
            title="Delete Download" if delete else "Downloaded Books",
            empty_text="No downloads",
        )

    def item_selected(self, item):
        return item

    async def left_pressed(self):
        return "AudiobookshelfLanding"

    async def right_pressed(self):
        return await self.center_pressed()


class LocalBooksPage(SelectDownloadedBookPage):
    """Compatibility route for older callers."""

    async def __init__(self):
        await super().__init__(delete=False)


class DeleteDownloadedBookPage(StaticTextPage, aobject):
    async def __init__(self, book_id: str, title: str, back_route="AudiobookshelfLanding"):
        self.book_id = book_id
        self.title = title
        self.back_route = back_route
        self.deleted = False
        StaticTextPage.__init__(self, f"Delete {title}?\n\nHold center to confirm.\nLeft to cancel.", text_size=14)

    async def center_held(self):
        if not self.deleted:
            active = self.manager.active_playback
            if active is not None and active.book.id == self.book_id:
                await self.manager.close_active_playback(suppress_errors=True)
            DownloadStore().delete(self.book_id)
            current = CONFIG.get("current_book")
            if current and current.get("book_id") == self.book_id:
                del CONFIG["current_book"]
                CONFIG.sync()
            self.deleted = True
            self.content = f"Deleted {self.title}."
            self.lines = self._wrap_text(self.content)
            self.scroll_offset = 0
            self._draw_text()
            return True

    async def left_pressed(self):
        return self.back_route
