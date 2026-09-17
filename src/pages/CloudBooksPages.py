from __future__ import annotations

from src.AudiobookModels import Book
from src.pages.ListPage import ListPage


def page_route(name: str, **kwargs):
    return name if not kwargs else (name, kwargs)


def book_destination(book: Book, download: bool, back_route):
    name = "DownloadBook" if download else "Player"
    data = {"book_id": book.id, "back_route": back_route}
    if not download:
        data["local"] = False
    return name, data


def grouped_entries(books: list[Book], download: bool, back_route):
    series = {}
    standalone = []
    for book in books:
        if book.series:
            for item in book.series:
                series[item.id] = item.name
        else:
            standalone.append(book)
    entries = [
        (
            f"Series: {name}",
            ("ChooseFromSeries", {"series_id": series_id, "series_name": name, "download": download, "back_route": back_route}),
        )
        for series_id, name in sorted(series.items(), key=lambda item: item[1].casefold())
    ]
    entries.extend(
        (book.title, book_destination(book, download, back_route))
        for book in sorted(standalone, key=lambda item: item.title.casefold())
    )
    return entries


class CloudListPage(ListPage):
    async def left_pressed(self):
        return self.back_route

    def item_selected(self, item):
        return item


class SelectCloudBookPage(CloudListPage):
    async def __init__(self, download: bool):
        self.download = download
        self.back_route = "AudiobookshelfLanding"
        route = page_route("SelectCloudBook", download=download)
        await super().__init__(
            items=[
                ("In Progress", page_route("SelectInProgressBook", download=download, back_route=route)),
                ("Recently Added", page_route("SelectRecentlyAdded", download=download, back_route=route)),
                ("All Series/Books", page_route("SelectAllBooks", download=download, back_route=route)),
                ("Select by Author", page_route("ChooseFromAuthor", download=download, back_route=route)),
                ("Select by Genre", page_route("ChooseFromGenre", download=download, back_route=route)),
            ],
            scrollable=True,
            title="Download Book" if download else "Stream Book",
        )


class BookResultsPage(CloudListPage):
    async def setup(self, books: list[Book], title: str, download: bool, back_route):
        self.download = download
        self.back_route = back_route
        own_route = self.route()
        await super().__init__(
            items=[(book.title, book_destination(book, download, own_route)) for book in books],
            scrollable=True,
            title=title,
            empty_text="No books found",
        )

    def route(self):
        raise NotImplementedError


class SelectInProgressBookPage(BookResultsPage):
    async def __init__(self, download=False, back_route="AudiobookshelfLanding"):
        self._route = page_route("SelectInProgressBook", download=download, back_route=back_route)
        await self.setup(await self.manager.api.get_in_progress_books(), "In Progress", download, back_route)

    def route(self):
        return self._route


class SelectRecentlyAddedPage(BookResultsPage):
    async def __init__(self, download=False, back_route="AudiobookshelfLanding"):
        self._route = page_route("SelectRecentlyAdded", download=download, back_route=back_route)
        await self.setup(await self.manager.api.get_recent_books(), "Recently Added", download, back_route)

    def route(self):
        return self._route


class SelectAllBooksPage(CloudListPage):
    async def __init__(self, download=False, back_route="AudiobookshelfLanding"):
        self.back_route = back_route
        own_route = page_route("SelectAllBooks", download=download, back_route=back_route)
        await super().__init__(
            items=grouped_entries(await self.manager.api.get_books(), download, own_route),
            scrollable=True,
            title="All Books",
            empty_text="No books found",
        )


class ChooseFromAuthorPage(CloudListPage):
    async def __init__(self, download=False, back_route="AudiobookshelfLanding"):
        self.back_route = back_route
        authors = await self.manager.api.get_authors()
        own_route = page_route("ChooseFromAuthor", download=download, back_route=back_route)
        await super().__init__(
            items=[
                (
                    author.get("name", "Unknown Author"),
                    page_route(
                        "ChooseAuthorBooks", author_id=author.get("id", ""),
                        author_name=author.get("name", "Unknown Author"),
                        download=download, back_route=own_route,
                    ),
                )
                for author in authors
            ],
            scrollable=True,
            title="Authors",
            empty_text="No authors found",
        )


class ChooseAuthorBooksPage(CloudListPage):
    async def __init__(self, author_id: str, author_name: str, download=False, back_route="ChooseFromAuthor"):
        self.back_route = back_route
        own_route = page_route(
            "ChooseAuthorBooks", author_id=author_id, author_name=author_name,
            download=download, back_route=back_route,
        )
        await super().__init__(
            items=grouped_entries(await self.manager.api.books_for_author(author_id), download, own_route),
            scrollable=True,
            title=author_name,
            empty_text="No books found",
            text_size=13,
        )


class ChooseFromGenrePage(CloudListPage):
    async def __init__(self, download=False, back_route="AudiobookshelfLanding"):
        self.back_route = back_route
        own_route = page_route("ChooseFromGenre", download=download, back_route=back_route)
        await super().__init__(
            items=[
                (genre, page_route("ChooseGenreBooks", genre=genre, download=download, back_route=own_route))
                for genre in await self.manager.api.get_genres()
            ],
            scrollable=True,
            title="Genres",
            empty_text="No genres found",
        )


class ChooseGenreBooksPage(CloudListPage):
    async def __init__(self, genre: str, download=False, back_route="ChooseFromGenre"):
        self.back_route = back_route
        own_route = page_route("ChooseGenreBooks", genre=genre, download=download, back_route=back_route)
        await super().__init__(
            items=grouped_entries(await self.manager.api.books_by_genre(genre), download, own_route),
            scrollable=True,
            title=genre,
            empty_text="No books found",
        )


class ChooseFromSeriesPage(BookResultsPage):
    async def __init__(self, series_id: str, series_name: str, download=False, back_route="SelectAllBooks"):
        self._route = page_route(
            "ChooseFromSeries", series_id=series_id, series_name=series_name,
            download=download, back_route=back_route,
        )
        await self.setup(await self.manager.api.books_in_series(series_id), series_name, download, back_route)

    def route(self):
        return self._route
