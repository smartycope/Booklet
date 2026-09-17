import asyncio

from src.AudiobookModels import Book, PlaybackSession, Track
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
