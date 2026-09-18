import asyncio
from pathlib import Path

from src import CONFIG, font
from src.GuiManager import GuiManager
from src.pages.LoadingPage import LoadingPage
from src.pages.Page import Page
from src.pages.ScreensaverPage import ScreensaverPage
from src.pages.SettingsPage import SettingsPage
from src.screens.Screen import Screen


class FakeScreen:
    def __init__(self):
        self.brightness = 0.5
        self.sleeping = False
        self.images = []

    def show_image(self, image, *_window):
        self.images.append(image)

    def sleep(self):
        self.sleeping = True

    def wake(self):
        self.sleeping = False


class FakePlayer:
    volume = 0.5


class FakePage(Page):
    def __init__(self):
        super().__init__()
        self.entered = False
        self.exited = False

    async def on_enter(self):
        self.entered = True

    async def on_exit(self):
        self.exited = True


def bare_manager(page):
    manager = GuiManager.__new__(GuiManager)
    manager._current_page = page
    manager.screen = FakeScreen()
    manager.player = FakePlayer()
    manager.small_font = font(11)
    manager._navigation_busy = False
    manager._event_busy = False
    manager._inactivity_task = None
    return manager


def test_settings_adjust_inline_and_offer_two_back_controls():
    manager = bare_manager(FakePage())
    Page.manager = manager
    CONFIG["volume"] = 0.5
    CONFIG["default_playback_speed"] = 1.0
    page = asyncio.run(SettingsPage())

    page._select_index(next(
        index for index, (_label, value) in enumerate(page.entries)
        if value == "volume"
    ))
    assert asyncio.run(page.right_pressed()) is True
    assert CONFIG["volume"] == 0.6
    assert manager.player.volume == 0.6

    page._select_index(next(
        index for index, (_label, value) in enumerate(page.entries)
        if value == "default_playback_speed"
    ))
    asyncio.run(page.right_pressed())
    assert CONFIG["default_playback_speed"] == 1.1
    assert asyncio.run(page.key2_pressed()) == "Landing"
    page._select_index(len(page.items) - 1)
    assert asyncio.run(page.center_pressed()) == "Landing"


def test_device_brightness_uses_a_logarithmic_curve():
    assert Screen._brightness_duty_cycle(0) == 0
    assert Screen._brightness_duty_cycle(1) == 0.5
    assert Screen._brightness_duty_cycle(0.5) < 0.25


def test_settings_check_for_updates_runs_git_pull_in_cwd(monkeypatch):
    calls = []

    class Process:
        returncode = 0

        async def communicate(self):
            return b"Already up to date.\n", None

    async def create_process(*args, **kwargs):
        calls.append((args, kwargs))
        return Process()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    manager = bare_manager(FakePage())
    Page.manager = manager
    page = asyncio.run(SettingsPage())
    page._select_index(page.entries.index(("Check for updates", "check_for_updates")))
    assert asyncio.run(page.center_pressed()) is True
    assert calls[0][0] == ("git", "pull")
    assert calls[0][1]["cwd"].resolve() == Path.cwd().resolve()
    assert page.update_status == "Already up to date."


def test_screensaver_preserves_and_restores_the_exact_page():
    async def exercise():
        previous = FakePage()
        manager = bare_manager(previous)
        await manager._screensaver_after(0)
        assert isinstance(manager.current_page, ScreensaverPage)
        assert manager.current_page.previous_page is previous
        assert manager.screen.sleeping is True
        assert previous.exited is False
        await manager.wake_from_screensaver()
        assert manager.current_page is previous
        assert manager.screen.sleeping is False
        manager._inactivity_task.cancel()

    asyncio.run(exercise())


def test_navigation_shows_loading_and_suppresses_duplicate_requests():
    async def exercise():
        previous = FakePage()
        manager = bare_manager(previous)
        gate = asyncio.Event()
        builds = 0

        async def build(_name, *_args, **_kwargs):
            nonlocal builds
            builds += 1
            await gate.wait()
            return FakePage()

        manager.page = build
        first = asyncio.create_task(manager.navigate_route("Slow"))
        await asyncio.sleep(0)
        assert isinstance(manager.current_page, LoadingPage)
        await manager.navigate_route("Slow")
        assert builds == 1
        gate.set()
        await first
        assert manager.current_page.entered is True
        manager._inactivity_task.cancel()

    asyncio.run(exercise())
