import asyncio

import src.GuiManager as gui_module
from src import CONFIG
from src.AudiobookModels import Book, Series
from src.pages.AudiobookshelfLandingPage import AudiobookshelfLandingPage
from src.pages.CloudBooksPages import (
    ChooseByAuthorPage, ChooseAuthorsBooksPage, SelectAllBooksPage,
    SelectCloudBookPage, SelectInProgressBookPage,
)
from src.pages.Page import Page


class FakeApi:
    def __init__(self):
        self.book_refreshes = []
        self.author_refreshes = []

    async def get_books(self, refresh=False):
        self.book_refreshes.append(refresh)
        return [
            Book(id="single", title="Standalone"),
            Book(id="series-book", title="Part One", series=[Series("series", "A Series", "1")]),
        ]

    async def get_authors(self, refresh=False):
        self.author_refreshes.append(refresh)
        return [{"id": "author", "name": "An Author"}]

    async def books_for_author(self, _author_id):
        return [Book(id="book", title="A Book")]


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
    assert page.items == ["Refresh Library", "Series: A Series", "Standalone"]
    assert page.entries[1][1][0] == "ChooseFromSeries"
    assert page.entries[2][1][0] == "Player"


def test_cloud_lists_use_right_to_select_and_left_to_return():
    Page.manager = FakeManager()
    page = asyncio.run(SelectCloudBookPage(download=False))
    assert asyncio.run(page.right_pressed()) == page.selected_value
    assert asyncio.run(page.left_pressed()) == "AudiobookshelfLanding"


def test_jump_controls_move_ten_items_and_between_letters():
    class ResultsApi(FakeApi):
        async def get_in_progress_books(self):
            return [Book(id=str(index), title=f"Book {index:02}") for index in range(25)]

        async def get_books(self, refresh=False):
            return [
                Book(id="a", title="Alpha"), Book(id="b1", title="Beta"),
                Book(id="b2", title="Bravo"), Book(id="c", title="Charlie"),
            ]

    manager = FakeManager()
    manager.api = ResultsApi()
    Page.manager = manager
    results = asyncio.run(SelectInProgressBookPage())
    asyncio.run(results.key3_pressed())
    assert results.selected_index == 10
    asyncio.run(results.key1_pressed())
    assert results.selected_index == 0

    all_books = asyncio.run(SelectAllBooksPage())
    all_books._select_index(all_books.items.index("Beta"))
    asyncio.run(all_books.key3_pressed())
    assert all_books.selected_item == "Charlie"
    asyncio.run(all_books.key1_pressed())
    assert all_books.selected_item == "Bravo"


def test_refresh_entry_requests_fresh_books():
    manager = FakeManager()
    manager.api = FakeApi()
    Page.manager = manager
    page = asyncio.run(SelectAllBooksPage(refresh=True))
    assert manager.api.book_refreshes == [True]
    assert page.entries[0][1][1]["refresh"] is True


def test_author_index_is_cached_and_refreshable_but_author_books_are_not_decorated():
    manager = FakeManager()
    manager.api = FakeApi()
    Page.manager = manager
    authors = asyncio.run(ChooseByAuthorPage(refresh=True))
    assert manager.api.author_refreshes == [True]
    assert authors.items == ["Refresh Library", "An Author"]
    assert authors.entries[1][1][0] == "ChooseAuthorsBooks"

    books = asyncio.run(ChooseAuthorsBooksPage("author", "An Author"))
    assert books.items == ["A Book"]


def test_all_audiobook_routes_are_registered():
    routes = {
        "AudiobookshelfLanding", "SelectCloudBook", "SelectInProgressBook",
        "SelectRecentlyAdded", "SelectAllBooks", "ChooseByAuthor",
        "ChooseAuthorsBooks", "ChooseFromGenre", "ChooseGenreBooks",
        "ChooseFromSeries", "SelectDownloadedBook", "DeleteDownloadedBook",
        "DownloadBook", "Player",
    }
    assert all(hasattr(gui_module, f"{route}Page") for route in routes)


def test_storage_size_is_human_readable():
    assert AudiobookshelfLandingPage._format_storage(5 * 1024**3) == "5.0 GB"


def test_audiobookshelf_landing_shows_online_status_and_cloud_options():
    Page.manager = FakeManager()
    page = asyncio.run(AudiobookshelfLandingPage())

    assert page.title == "Audiobookshelf (Online)"
    assert "Download a Book" in page.items
    assert "Stream a Book" in page.items


def test_audiobookshelf_landing_offline_only_offers_local_actions():
    manager = FakeManager()
    manager.api = None
    Page.manager = manager
    CONFIG["current_book"] = {
        "book_id": "streamed",
        "title": "Streamed Book",
        "local": False,
    }
    page = asyncio.run(AudiobookshelfLandingPage())

    assert page.title == "Audiobookshelf (Offline)"
    assert "Resume Streamed Book" not in page.items
    assert "Download a Book" not in page.items
    assert "Stream a Book" not in page.items
    assert "Play Downloaded Book" in page.items
    assert "Delete Downloaded Book" in page.items
    assert "Login failed: check server and API key" in page.items


def test_audiobookshelf_landing_explains_530_response():
    class ResponseError(Exception):
        status = 530

    manager = FakeManager()
    manager.api = None
    manager.api_error = ResponseError()
    Page.manager = manager

    page = asyncio.run(AudiobookshelfLandingPage())

    assert "Login failed: server may be down (530)" in page.items
