import asyncio
import inspect
from pathlib import Path
from types import SimpleNamespace
import zipfile

import pytest

from src import font
from src.AudiobookModels import Book, Track
from src.DownloadStore import DownloadStore
from src.pages.DownloadBookPage import DownloadBookPage
from src.pages.Page import Page


class ZipApi:
    def __init__(self, unsafe=False):
        self.unsafe = unsafe

    async def download_book(self, _book_id, destination, progress):
        with zipfile.ZipFile(destination, "w") as archive:
            archive.writestr("../escape.mp3" if self.unsafe else "disc/02.mp3", b"two")
            if not self.unsafe:
                archive.writestr("disc/01.mp3", b"one")
        if progress:
            result = progress(destination.stat().st_size, destination.stat().st_size)
            if inspect.isawaitable(result):
                await result
        return "book.zip", "application/zip"


def test_download_is_atomic_and_manifest_tracks_server_order(tmp_path):
    store = DownloadStore(tmp_path)
    book = Book(
        id="book-id", title="Book", duration=20,
        tracks=[Track("01.mp3", "", 10, 0), Track("02.mp3", "", 10, 10)],
    )
    updates = []
    downloaded = asyncio.run(store.download(ZipApi(), book, lambda current, total: updates.append((current, total))))
    assert downloaded.title == "Book"
    assert [Path(track.source).name for track in downloaded.tracks] == ["01.mp3", "02.mp3"]
    assert store.contains("book-id")
    assert updates[-1][0] == updates[-1][1]
    assert not list(tmp_path.glob(".book-id-*"))


def test_download_rejects_zip_path_traversal_and_cleans_partial_files(tmp_path):
    store = DownloadStore(tmp_path)
    with pytest.raises(RuntimeError, match="Unsafe path"):
        asyncio.run(store.download(ZipApi(unsafe=True), Book(id="book-id", title="Book")))
    assert not store.book_dir("book-id").exists()
    assert not (tmp_path.parent / "escape.mp3").exists()


def test_delete_only_removes_requested_book(tmp_path):
    store = DownloadStore(tmp_path)
    first = store.book_dir("first")
    second = store.book_dir("second")
    first.mkdir(parents=True)
    second.mkdir()
    store.delete("first")
    assert not first.exists()
    assert second.exists()


def test_download_size_uses_binary_human_readable_units():
    assert DownloadBookPage._format_size(512) == "512 bytes"
    assert DownloadBookPage._format_size(1536) == "1.5 KB"
    assert DownloadBookPage._format_size(2 * 1024 * 1024) == "2.0 MB"


def test_download_estimate_uses_observed_transfer_speed():
    page = SimpleNamespace(
        total=1000,
        downloaded=400,
        _progress_samples=[(10.0, 0), (12.0, 400)],
    )
    assert DownloadBookPage._estimated_seconds_remaining(page) == 3
    assert DownloadBookPage._format_duration(3665) == "1h 1m"


def test_available_bytes_uses_nearest_existing_download_parent(tmp_path, monkeypatch):
    requested = []

    def disk_usage(path):
        requested.append(path)
        return SimpleNamespace(free=123456)

    monkeypatch.setattr("src.DownloadStore.shutil.disk_usage", disk_usage)
    store = DownloadStore(tmp_path / "not-created" / "Audiobooks")
    assert store.available_bytes() == 123456
    assert requested == [tmp_path]


def test_download_page_does_not_start_when_book_will_not_fit():
    class Api:
        async def get_book(self, _book_id):
            return Book(id="large", title="Large Book", size=2 * 1024**3)

    class Store:
        def contains(self, _book_id):
            return False

        def available_bytes(self):
            return 512 * 1024**2

        async def download(self, *_args, **_kwargs):
            raise AssertionError("download must not start")

    renders = []
    manager = SimpleNamespace(
        api=Api(),
        small_font=font(11),
        current_page=None,
        render=lambda: renders.append(True),
    )
    Page.manager = manager
    page = asyncio.run(DownloadBookPage("large"))
    manager.current_page = page
    page.store = Store()

    asyncio.run(page.on_enter())

    assert page.insufficient_space is True
    assert page.active is False
    assert page._task is None
    assert page._insufficient_space_status() == (
        "Not enough space\nBook: 2.0 GB\nAvailable: 512.0 MB\nLeft to return"
    )
    assert renders == [True]
