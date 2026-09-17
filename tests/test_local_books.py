import asyncio
import importlib

from src.AudiobookModels import Book


local_books_module = importlib.import_module("src.pages.LocalBooksPage")


def test_delete_download_list_and_confirmation_show_book_size(monkeypatch):
    class Store:
        def list_books(self):
            return [Book(id="book", title="A Book", size=1536 * 1024)]

    original_store = local_books_module.DownloadStore
    Store.format_size = staticmethod(original_store.format_size)
    monkeypatch.setattr(local_books_module, "DownloadStore", Store)

    page = asyncio.run(local_books_module.SelectDownloadedBookPage(delete=True))
    assert page.items == ["A Book (1.5 MB)"]
    route, payload = page.selected_value
    assert route == "DeleteDownloadedBook"
    assert payload["size"] == 1536 * 1024

    confirmation = asyncio.run(local_books_module.DeleteDownloadedBookPage(**payload))
    assert "Size: 1.5 MB" in confirmation.content
