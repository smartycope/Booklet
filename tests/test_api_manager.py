import asyncio
from pathlib import Path
from types import SimpleNamespace

from src.AudiobookshelfApiManager import AudiobookshelfApiManager


class FakeContent:
    async def iter_chunked(self, _size):
        yield b"abc"
        yield b"def"


class FakeResponse:
    status = 200
    content_length = 6
    headers = {
        "Content-Disposition": 'attachment; filename="book.m4b"',
        "Content-Type": "audio/mp4",
    }
    content = FakeContent()

    async def __aenter__(self): return self
    async def __aexit__(self, *_args): pass
    def raise_for_status(self): pass


class FakeSession:
    def __init__(self):
        self.url = None
        self.headers = None

    def get(self, url, headers):
        self.url, self.headers = url, headers
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.updated = None
        self.synced = None
        self.closed = None

    async def get_my_media_progress(self, **_kwargs):
        return SimpleNamespace(current_time=42.5)

    async def update_my_media_progress(self, **kwargs):
        self.updated = kwargs

    async def get_library_item_book(self, **_kwargs):
        return {
            "id": "book",
            "media": {
                "metadata": {"title": "Example", "authors": [{"name": "Author"}]},
                "duration": 100,
                "tracks": [{"title": "file.mp3", "contentUrl": "/s/item/book/file.mp3", "duration": 100}],
                "chapters": [{"title": "One", "start": 0, "end": 100}],
            },
        }

    async def get_playback_session(self, **_kwargs):
        return SimpleNamespace(
            id_="session", current_time=12, duration=100,
            audio_tracks=[SimpleNamespace(
                title="file.mp3", content_url="/s/item/book/file.mp3",
                duration=100, start_offset=0, mime_type="audio/mpeg",
            )],
            chapters=[SimpleNamespace(title="One", start=0, end=100)],
        )

    async def sync_open_session(self, **kwargs): self.synced = kwargs
    async def close_open_session(self, **kwargs): self.closed = kwargs

    async def get_library_authors(self, **_kwargs):
        self.author_calls = getattr(self, "author_calls", 0) + 1
        return [SimpleNamespace(id_="author", name="Author")]


def manager():
    return AudiobookshelfApiManager(
        FakeClient(), "library", FakeSession(),
        host="https://example.test", token="secret token",
    )


def test_media_progress_uses_supported_client_methods():
    api = manager()
    assert asyncio.run(api.get_media_progress("book")) == 42.5
    asyncio.run(api.update_media_progress("book", 50, 100))
    assert api.client.updated["progress_seconds"] == 50
    assert api.client.updated["duration_seconds"] == 100


def test_playback_session_normalizes_tracks_and_authenticates_stream_url():
    api = manager()
    session = asyncio.run(api.start_playback("book"))
    assert session.id == "session"
    assert session.current_time == 12
    assert session.book.title == "Example"
    assert session.book.tracks[0].source == "https://example.test/s/item/book/file.mp3?token=secret+token"


def test_download_streams_to_file_with_progress(tmp_path):
    api = manager()
    destination = tmp_path / "book.part"
    progress = []
    filename, content_type = asyncio.run(
        api.download_book("book", destination, lambda current, total: progress.append((current, total)))
    )
    assert destination.read_bytes() == b"abcdef"
    assert filename == "book.m4b"
    assert content_type == "audio/mp4"
    assert progress == [(3, 6), (6, 6)]
    assert api.session.headers == {"Authorization": "Bearer secret token"}


def test_book_list_is_cached_until_refresh(monkeypatch):
    import src.AudiobookshelfApiManager as api_module

    class LibraryClient(FakeClient):
        def __init__(self):
            super().__init__()
            self.calls = 0

        async def get_library_items(self, **_kwargs):
            self.calls += 1
            yield SimpleNamespace(results=[{
                "id": "book", "mediaType": "book",
                "media": {"metadata": {"title": "Cached"}},
            }])

    monkeypatch.setattr(api_module, "LibraryItemMinifiedBook", object)
    client = LibraryClient()
    api = AudiobookshelfApiManager(client, "library", FakeSession(), host="https://example.test", token="token")
    assert asyncio.run(api.get_books())[0].title == "Cached"
    assert asyncio.run(api.get_books())[0].title == "Cached"
    assert client.calls == 1
    asyncio.run(api.get_books(refresh=True))
    assert client.calls == 2


def test_author_index_is_cached_until_refresh():
    api = manager()
    assert asyncio.run(api.get_authors())[0]["name"] == "Author"
    asyncio.run(api.get_authors())
    assert api.client.author_calls == 1
    asyncio.run(api.get_authors(refresh=True))
    assert api.client.author_calls == 2


def test_book_normalizes_media_size():
    from src.AudiobookModels import Book
    assert Book.from_api({"id": "book", "media": {"size": 12345}}).size == 12345
