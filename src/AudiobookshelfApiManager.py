from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit

import aiohttp
import aioaudiobookshelf as abs
from aioaudiobookshelf import SessionConfiguration, UserClient
from aioaudiobookshelf.schema.library import LibraryItemMinifiedBook
from aioaudiobookshelf.schema.calls_items import PlayParameters
from aioaudiobookshelf.schema.calls_session import CloseOpenSessionsParameters
from aioaudiobookshelf.schema.session import DeviceInfo

from src import CONFIG, KEYS, AUDIOBOOKSHELF_API_BASE as HOST
from src.AudiobookModels import Book, PlaybackSession, value


class AudiobookshelfApiManager:
    pagination_items_per_page = 30

    def __init__(
        self,
        client,
        library_id: str,
        session: aiohttp.ClientSession,
        host: str = HOST,
        token: str | None = None,
    ):
        self.client = client
        self.library_id = library_id
        self.session = session
        self.host = host.rstrip("/") + "/"
        self.token = token or KEYS["audiobookshelf_api_key"]
        self._books_cache: list[Book] | None = None
        self._authors_cache: list[dict[str, Any]] | None = None

    @classmethod
    async def create(cls, session: aiohttp.ClientSession):
        token = KEYS["audiobookshelf_api_key"]
        client = await abs.get_user_client_by_token(
            session_config=SessionConfiguration(
                session=session,
                url=HOST,
                pagination_items_per_page=cls.pagination_items_per_page,
                token=token,
            )
        )
        library_id = CONFIG.get("library_id")
        if library_id is None:
            library_id = await cls._find_library_id(client)
        return cls(client, library_id, session, HOST, token)

    @staticmethod
    async def _find_library_id(client: UserClient):
        for library in await client.get_all_libraries():
            if library.name == KEYS["audiobookshelf_library_name"]:
                CONFIG["library_id"] = library.id_
                CONFIG.sync()
                return library.id_
        raise RuntimeError("Configured Audiobookshelf library was not found")

    def _url(self, path: str) -> str:
        return urljoin(self.host, path.lstrip("/"))

    async def _request(self, method: str, path: str, *, allow_not_found=False, **kwargs):
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {self.token}"
        async with self.session.request(method, self._url(path), headers=headers, **kwargs) as response:
            if allow_not_found and response.status == 404:
                return None
            response.raise_for_status()
            if response.status == 204 or response.content_length == 0:
                return None
            return await response.json()

    async def get_books(self, in_progress=False, expanded=False, refresh=False) -> list[Book]:
        if in_progress:
            return await self.get_in_progress_books()
        if self._books_cache is None or refresh:
            books = []
            async for response in self.client.get_library_items(library_id=self.library_id):
                if not response.results:
                    break
                books.extend(
                    Book.from_api(item)
                    for item in response.results
                    if isinstance(item, LibraryItemMinifiedBook)
                )
            self._books_cache = books
        books = list(self._books_cache)
        if expanded:
            return [await self.get_book(book.id) for book in books]
        return books

    async def get_in_progress_books(self) -> list[Book]:
        data = await self._request("GET", "/api/me/items-in-progress", params={"limit": 1000})
        return [
            Book.from_api(item)
            for item in data.get("libraryItems", [])
            if value(item, "mediaType", "media_type", default="book") == "book"
        ]

    async def get_recent_books(self) -> list[Book]:
        return sorted(await self.get_books(), key=lambda book: book.added_at, reverse=True)

    async def get_book(self, book_id: str) -> Book:
        data = await self.client.get_library_item_book(book_id=book_id, expanded=True)
        book = Book.from_api(data)
        if not book.id:
            book.id = book_id
        return book

    async def get_authors(self, refresh=False) -> list[dict[str, Any]]:
        if self._authors_cache is None or refresh:
            authors = await self.client.get_library_authors(library_id=self.library_id)
            normalized = [
                {"id": value(author, "id_", "id", default=""), "name": value(author, "name", default="Unknown Author")}
                for author in authors
            ]
            self._authors_cache = sorted(normalized, key=lambda author: author["name"].casefold())
        return [dict(author) for author in self._authors_cache]

    async def get_filter_data(self) -> dict[str, Any]:
        data = await self.client.get_library_filterdata(library_id=self.library_id)
        return {
            "genres": list(value(data, "genres", default=[]) or []),
            "series": list(value(data, "series", default=[]) or []),
        }

    async def get_genres(self) -> list[str]:
        data = await self.get_filter_data()
        genres = data.get("genres", [])
        normalized = [genre.get("name", genre.get("genre", "")) if isinstance(genre, dict) else genre for genre in genres]
        return sorted(filter(None, normalized), key=str.casefold)

    async def get_series(self) -> list[dict[str, Any]]:
        data = await self._request(
            "GET", f"/api/libraries/{self.library_id}/series",
            params={"limit": 0, "sort": "name"},
        )
        return sorted(data.get("results", data.get("series", [])), key=lambda item: item.get("name", "").casefold())

    async def books_for_author(self, author_id: str) -> list[Book]:
        data = await self.client.get_author(author_id=author_id, include_items=True, include_series=True)
        items = value(data, "library_items", "libraryItems", default=[]) or []
        return sorted((Book.from_api(item) for item in items), key=lambda book: book.title.casefold())

    async def books_by_genre(self, genre: str) -> list[Book]:
        return sorted(
            (book for book in await self.get_books() if genre.casefold() in {item.casefold() for item in book.genres}),
            key=lambda book: book.title.casefold(),
        )

    async def books_in_series(self, series_id: str) -> list[Book]:
        books = [book for book in await self.get_books() if any(series.id == series_id for series in book.series)]
        return sorted(books, key=lambda book: self._sequence_key(next((s.sequence for s in book.series if s.id == series_id), None)))

    @staticmethod
    def _sequence_key(sequence: str | None):
        try:
            return (0, float(sequence))
        except (TypeError, ValueError):
            return (1, str(sequence or ""))

    async def get_media_progress(self, book_id: str) -> float:
        data = await self.client.get_my_media_progress(item_id=book_id)
        return float(value(data, "current_time", "currentTime", default=0) or 0)

    async def update_media_progress(self, book_id: str, current_time: float, duration: float, finished=False):
        await self.client.update_my_media_progress(
            item_id=book_id,
            duration_seconds=duration,
            progress_seconds=current_time,
            is_finished=bool(finished),
        )

    async def start_playback(self, book_id: str) -> PlaybackSession:
        # Fetch metadata first so a metadata failure cannot leave an open
        # playback session behind on the server.
        book = await self.get_book(book_id)
        data = await self.client.get_playback_session(
            item_id=book_id,
            session_parameters=PlayParameters(
                device_info=DeviceInfo(
                    device_id="booklet", client_name="Booklet", client_version="1",
                    manufacturer="Raspberry Pi", model="Booklet",
                ),
                force_direct_play=True,
                supported_mime_types=[
                    "audio/aac", "audio/flac", "audio/mp4", "audio/mpeg",
                    "audio/ogg", "audio/opus", "audio/wav", "audio/x-m4a",
                ],
                media_player="vlc",
            ),
        )
        if not book.id:
            book.id = book_id
        audio_tracks = value(data, "audio_tracks", "audioTracks", default=[]) or []
        chapters = value(data, "chapters", default=[]) or []
        if audio_tracks:
            media = {
                "metadata": {"title": book.title},
                "tracks": audio_tracks,
                "chapters": chapters,
            }
            session_book = Book.from_api({"id": book.id, "media": media})
            session_book.authors, session_book.genres = book.authors, book.genres
            session_book.series, session_book.added_at = book.series, book.added_at
            book = session_book
        for track in book.tracks:
            track.source = self.authenticated_url(track.source)
        duration = float(value(data, "duration", default=book.duration) or book.duration)
        book.duration = duration
        return PlaybackSession(
            id=str(value(data, "id_", "id")), book=book,
            current_time=float(value(data, "current_time", "currentTime", default=0) or 0), duration=duration,
        )

    async def sync_session(self, session_id: str, current_time: float, duration: float, time_listened: float):
        await self.client.sync_open_session(
            session_id=session_id,
            parameters=CloseOpenSessionsParameters(
                current_time=current_time, duration=duration,
                time_listened=max(0, time_listened),
            ),
        )

    async def close_session(self, session_id: str, current_time: float, duration: float, time_listened: float = 0):
        await self.client.close_open_session(
            session_id=session_id,
            parameters=CloseOpenSessionsParameters(
                current_time=current_time, duration=duration,
                time_listened=max(0, time_listened),
            ),
        )

    def authenticated_url(self, path: str) -> str:
        parts = urlsplit(self._url(path))
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query.setdefault("token", self.token)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

    async def download_book(
        self, book_id: str, destination: Path,
        progress: Callable[[int, int | None], Any] | None = None,
    ) -> tuple[str, str]:
        headers = {"Authorization": f"Bearer {self.token}"}
        async with self.session.get(self._url(f"/api/items/{book_id}/download"), headers=headers) as response:
            response.raise_for_status()
            total = response.content_length
            filename = self._content_disposition_filename(response.headers.get("Content-Disposition", "")) or f"{book_id}.download"
            downloaded = 0
            with destination.open("wb") as output:
                async for chunk in response.content.iter_chunked(128 * 1024):
                    output.write(chunk)
                    downloaded += len(chunk)
                    if progress is not None:
                        result = progress(downloaded, total)
                        if inspect.isawaitable(result):
                            await result
            return filename, response.headers.get("Content-Type", "").split(";", 1)[0]

    @staticmethod
    def _content_disposition_filename(disposition: str) -> str | None:
        for part in disposition.split(";"):
            key, separator, raw_value = part.strip().partition("=")
            if separator and key.casefold() in {"filename", "filename*"}:
                text = raw_value.strip('"')
                if "''" in text:
                    text = text.split("''", 1)[1]
                return Path(unquote(text)).name
        return None
