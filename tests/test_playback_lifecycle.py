import asyncio

from src import CONFIG
from src.AudiobookModels import Book, PlaybackSession, Track
import src.GuiManager as gui_module
from src.GuiManager import GuiManager


class FakePlayer:
    def __init__(self):
        self.position = 0
        self.duration = 60
        self.is_playing = False
        self.loaded = None

    def load(self, tracks, chapters, start):
        self.loaded = (tracks, chapters, start)
        self.position = start

    def play(self): self.is_playing = True
    def pause(self): self.is_playing = False
    def stop(self): self.is_playing = False
    def close(self): pass


class FakeApi:
    def __init__(self):
        self.synced = []
        self.closed = []

    async def start_playback(self, book_id):
        book = Book(id=book_id, title=f"Book {book_id}", duration=60, tracks=[Track("audio", "url", 60)])
        return PlaybackSession(f"session-{book_id}", book, 10, 60)

    async def sync_session(self, *args): self.synced.append(args)
    async def close_session(self, *args): self.closed.append(args)


def manager():
    result = GuiManager.__new__(GuiManager)
    result.player = FakePlayer()
    result.api = FakeApi()
    result.active_playback = None
    return result


def test_leaving_pauses_and_syncs_but_keeps_session_open():
    gui = manager()
    asyncio.run(gui.activate_book("one", False, "Previous"))
    asyncio.run(gui.pause_active_playback())
    assert gui.active_playback.session_id == "session-one"
    assert gui.player.is_playing is False
    assert gui.api.synced
    assert gui.api.closed == []


def test_starting_different_book_closes_previous_session():
    gui = manager()
    asyncio.run(gui.activate_book("one", False, "Previous"))
    asyncio.run(gui.activate_book("two", False, "Previous"))
    assert gui.api.closed[0][0] == "session-one"
    assert gui.active_playback.book.id == "two"


def test_book_speed_uses_saved_value_or_default():
    gui = manager()
    CONFIG["playback_speeds"] = {"one": 1.7}
    CONFIG["default_playback_speed"] = 1.2
    asyncio.run(gui.activate_book("one", False, "Previous"))
    assert gui.player.rate == 1.7
    asyncio.run(gui.activate_book("two", False, "Previous"))
    assert gui.player.rate == 1.2


def test_persist_playback_speed_is_keyed_by_book():
    gui = manager()
    CONFIG["playback_speeds"] = {"other": 1.1}
    gui.persist_playback_speed("book", 1.6)
    assert CONFIG["playback_speeds"] == {"other": 1.1, "book": 1.6}


def test_downloaded_book_plays_offline_from_local_position(monkeypatch):
    gui = manager()
    gui.api = None
    book = Book(
        id="local",
        title="Downloaded Book",
        duration=60,
        tracks=[Track("audio", "/tmp/audio.mp3", 60)],
    )
    monkeypatch.setattr(gui_module, "DownloadStore", lambda: type(
        "Store", (), {"load": lambda self, _book_id: book}
    )())
    CONFIG["local_positions"] = {"local": 23}

    asyncio.run(gui.activate_book("local", True, "Previous"))

    assert gui.player.loaded[2] == 23
    assert gui.active_playback.local is True


def test_offline_local_sync_still_persists_position():
    gui = manager()
    gui.api = None
    gui.active_playback = type("Context", (), {
        "book": Book(id="local", title="Downloaded Book", duration=60),
        "local": True,
        "session_id": None,
        "was_playing": False,
        "pending_listened": 0.0,
        "last_sync_at": 0.0,
    })()
    gui.player.position = 17

    asyncio.run(gui.sync_active_playback())

    assert CONFIG["local_positions"]["local"] == 17
