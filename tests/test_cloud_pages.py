import asyncio

import src.GuiManager as gui_module
from src.AudiobookModels import Book, Series
from src.pages.CloudBooksPages import SelectAllBooksPage, SelectCloudBookPage
from src.pages.Page import Page


class FakeApi:
    async def get_books(self):
        return [
            Book(id="single", title="Standalone"),
            Book(id="series-book", title="Part One", series=[Series("series", "A Series", "1")]),
        ]


class FakeManager:
    api = FakeApi()


def test_cloud_landing_branches_preserve_download_mode():
    Page.manager = FakeManager()
    page = asyncio.run(SelectCloudBookPage(download=True))
    assert page.items == ["In Progress", "Recently Added", "All Series/Books", "Select by Author", "Select by Genre"]
    assert page.entries[0][1][1]["download"] is True


def test_all_books_collapses_series_but_keeps_standalone_books():
    Page.manager = FakeManager()
    page = asyncio.run(SelectAllBooksPage(download=False, back_route="SelectCloudBook"))
    assert page.items == ["Series: A Series", "Standalone"]
    assert page.entries[0][1][0] == "ChooseFromSeries"
    assert page.entries[1][1][0] == "Player"


def test_all_audiobook_routes_are_registered():
    routes = {
        "AudiobookshelfLanding", "SelectCloudBook", "SelectInProgressBook",
        "SelectRecentlyAdded", "SelectAllBooks", "ChooseFromAuthor",
        "ChooseAuthorBooks", "ChooseFromGenre", "ChooseGenreBooks",
        "ChooseFromSeries", "SelectDownloadedBook", "DeleteDownloadedBook",
        "DownloadBook", "Player",
    }
    assert all(hasattr(gui_module, f"{route}Page") for route in routes)
