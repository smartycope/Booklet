import asyncio
from functools import partial
import logging
import time
from src import CONFIG, font, pages
from src.AudiobookModels import PlaybackContext
from src.DownloadStore import DownloadStore
from src.pages.ErrorPage import ErrorPage
from src.pages.Page import Page
from src.AudioPlayer import AudioPlayer
from src.AudiobookshelfApiManager import AudiobookshelfApiManager
from src.screens.BaseScreen import BaseScreen

from src.pages.AudiobookshelfLandingPage import AudiobookshelfLandingPage
from src.pages.BluetoothPage import BluetoothPage
from src.pages.LandingPage import LandingPage
from src.pages.LocalBooksPage import LocalBooksPage
from src.pages.LocalBooksPage import DeleteDownloadedBookPage, SelectDownloadedBookPage
from src.pages.SelectBookPage import SelectBookPage
from src.pages.CloudBooksPages import (
    ChooseAuthorsBooksPage,
    ChooseByAuthorPage,
    ChooseFromGenrePage,
    ChooseFromSeriesPage,
    ChooseGenreBooksPage,
    SelectAllBooksPage,
    SelectCloudBookPage,
    SelectRecentlyAddedPage,
    SelectInProgressBookPage,
)
from src.pages.DownloadBookPage import DownloadBookPage
from src.pages.LoadingPage import LoadingPage
from src.pages.ScreensaverPage import ScreensaverPage
from src.pages.SettingsPage import SettingsPage
from src.pages.StaticTextPage import StaticTextPage
from src.pages.VolumePage import VolumePage
from src.pages.BrightnessPage import BrightnessPage
from src.pages.PlayerPage import PlayerPage

class GuiManager:
    """ Manage the connection between the screen and the pages. Handles events, and switches between pages. """
    def __init__(
        self,
        player: AudioPlayer,
        api: AudiobookshelfApiManager | None,
        screen: BaseScreen,
        first_page: Page,
        api_error: Exception | None = None,
    ):
        self.player = player
        self.api = api
        self.api_error = api_error
        self.screen = screen
        self.pages = pages
        self.small_font = font(11)
        self.active_playback: PlaybackContext | None = None
        self._navigation_busy = False
        self._event_busy = False
        self._inactivity_task = None

        self._current_page = first_page

        self.loop = asyncio.get_running_loop()

        # Connect all the events
        self.screen.gpio_key_up_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key_down_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key_left_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key_right_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key_center_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key1_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key2_pin.when_pressed = partial(self.dispatch_event, event='pressed')
        self.screen.gpio_key3_pin.when_pressed = partial(self.dispatch_event, event='pressed')

        self.screen.gpio_key_up_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key_down_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key_left_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key_right_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key_center_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key1_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key2_pin.when_released = partial(self.dispatch_event, event='released')
        self.screen.gpio_key3_pin.when_released = partial(self.dispatch_event, event='released')

        self.screen.gpio_key_up_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key_down_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key_left_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key_right_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key_center_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key1_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key2_pin.when_held = partial(self.dispatch_event, event='held')
        self.screen.gpio_key3_pin.when_held = partial(self.dispatch_event, event='held')

        Page.manager = self
        self.player.volume = CONFIG.get("volume", 1.0)
        self.render()
        self.reset_screensaver_timer()


    def dispatch_event(self, device, event=None):
        future = asyncio.run_coroutine_threadsafe(
            self.handle_event(device, event),
            self.loop,
        )
        future.add_done_callback(self._event_finished)

    def _event_finished(self, future):
        if future.cancelled():
            return
        exception = future.exception()
        if exception is not None:
            logging.exception(
                "Button event failed",
                exc_info=(type(exception), exception, exception.__traceback__),
            )
            asyncio.run_coroutine_threadsafe(self.navigate(ErrorPage(exception)), self.loop)

    async def handle_event(self, device, event=None):
        if isinstance(self.current_page, ScreensaverPage):
            await self.wake_from_screensaver()
            return
        self.reset_screensaver_timer()
        if self._navigation_busy or self._event_busy:
            return
        self._event_busy = True
        try:
            await self._handle_event(device, event)
        finally:
            self._event_busy = False
            self.reset_screensaver_timer()

    async def _handle_event(self, device, event=None):
        match event:
            case 'pressed':
                match device:
                    case self.screen.gpio_key_up_pin:     rtn = await self.current_page.up_pressed()
                    case self.screen.gpio_key_down_pin:   rtn = await self.current_page.down_pressed()
                    case self.screen.gpio_key_left_pin:   rtn = await self.current_page.left_pressed()
                    case self.screen.gpio_key_right_pin:  rtn = await self.current_page.right_pressed()
                    case self.screen.gpio_key_center_pin: rtn = await self.current_page.center_pressed()
                    case self.screen.gpio_key1_pin:       rtn = await self.current_page.key1_pressed()
                    case self.screen.gpio_key2_pin:       rtn = await self.current_page.key2_pressed()
                    case self.screen.gpio_key3_pin:       rtn = await self.current_page.key3_pressed()
                    case _:
                        raise ValueError(f"Unknown device: {device}")
            case 'released':
                match device:
                    case self.screen.gpio_key_up_pin:     rtn = await self.current_page.up_released()
                    case self.screen.gpio_key_down_pin:   rtn = await self.current_page.down_released()
                    case self.screen.gpio_key_left_pin:   rtn = await self.current_page.left_released()
                    case self.screen.gpio_key_right_pin:  rtn = await self.current_page.right_released()
                    case self.screen.gpio_key_center_pin: rtn = await self.current_page.center_released()
                    case self.screen.gpio_key1_pin:       rtn = await self.current_page.key1_released()
                    case self.screen.gpio_key2_pin:       rtn = await self.current_page.key2_released()
                    case self.screen.gpio_key3_pin:       rtn = await self.current_page.key3_released()
                    case _:
                        raise ValueError(f"Unknown device: {device}")
            case 'held':
                match device:
                    case self.screen.gpio_key_up_pin:     rtn = await self.current_page.up_held()
                    case self.screen.gpio_key_down_pin:   rtn = await self.current_page.down_held()
                    case self.screen.gpio_key_left_pin:   rtn = await self.current_page.left_held()
                    case self.screen.gpio_key_right_pin:  rtn = await self.current_page.right_held()
                    case self.screen.gpio_key_center_pin: rtn = await self.current_page.center_held()
                    case self.screen.gpio_key1_pin:       rtn = await self.current_page.key1_held()
                    case self.screen.gpio_key2_pin:       rtn = await self.current_page.key2_held()
                    case self.screen.gpio_key3_pin:       rtn = await self.current_page.key3_held()
                    case _:
                        raise ValueError(f"Unknown device: {device}")
            case _:
                raise ValueError(f"Unknown event: {event}")

        # If the handler returns a string, goto that page
        # using type is intentional here: returns are almost always going to be literal
        # This is a string and not an instantiated Page because that would be a circular import
        # (Landing -> Settings, but also Settings -> Landing)
        if type(rtn) is str:
            await self.navigate_route(rtn)
        elif isinstance(rtn, tuple):
            # If the handler returns a tuple of a string and a dictionary, goto that page, and set those
            # attributes on the page class
            if type(rtn[0]) is str and type(rtn[1]) is dict:
                await self.navigate_route(rtn[0], **rtn[1])
            # If the handler returns a tuple of 4 integers, partial update (should be a tuple of 4 integers)
            # x1, x2, y1, y2
            elif len(rtn) == 4:
                self.render(rtn)
            else:
                raise ValueError(f"Invalid tuple: {rtn}")
        # If the handler returns True, render the current page
        elif rtn is True:
            self.render()
        # If the handler returns None, no modifications to self.current_page.img were made
        elif rtn not in (False, None):
            raise ValueError(f"Invalid return value from event handler: `{rtn}` on page `{self.current_page.__class__.__name__}` for event `{event}` on device {device}")

    def render(self, window=()):
        self.screen.show_image(self.current_page.img, *window)

    async def navigate_route(self, name, *args, **kwargs):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        previous_page = self.current_page
        self._current_page = LoadingPage()
        self.render()
        try:
            await previous_page.on_exit()
            page = await self.page(name, *args, **kwargs)
            self.current_page = page
            await page.on_enter()
        finally:
            self._navigation_busy = False
            self.reset_screensaver_timer()

    async def navigate(self, page: Page):
        await self.current_page.on_exit()
        self.current_page = page
        await page.on_enter()
        self.reset_screensaver_timer()

    def reset_screensaver_timer(self):
        task = self._inactivity_task
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()
        timeout = max(1.0, float(CONFIG.get("screensaver_timeout", 30)))
        self._inactivity_task = asyncio.create_task(self._screensaver_after(timeout))

    async def _screensaver_after(self, timeout):
        try:
            await asyncio.sleep(timeout)
        except asyncio.CancelledError:
            return
        if self._navigation_busy or self._event_busy or isinstance(
            self.current_page, (DownloadBookPage, BluetoothPage, ScreensaverPage, LoadingPage)
        ):
            return
        previous_page = self.current_page
        self._current_page = ScreensaverPage(previous_page)
        self.render()
        sleep = getattr(self.screen, "sleep", None)
        if sleep is not None:
            sleep()

    async def wake_from_screensaver(self):
        if not isinstance(self.current_page, ScreensaverPage):
            return
        previous_page = self.current_page.previous_page
        wake = getattr(self.screen, "wake", None)
        if wake is not None:
            wake()
        self._current_page = previous_page
        self.render()
        self.reset_screensaver_timer()

    # We do this to avoid circular imports
    @staticmethod
    async def page(name, *args, **kwargs) -> Page:
        """ Initialize a page by name (without the 'Page' suffix)
            args and kwargs are passed to the constructor verbatim
        """
        return await globals()[name+'Page'](*args, **kwargs)


    @property
    def current_page(self) -> Page:
        # return pages[self.current_page_name]
        return self._current_page

    @current_page.setter
    def current_page(self, page:Page):
        self._current_page = page
        # print(f"Navigating to {self._current_page.__class__.__name__}")
        self.render()

    async def activate_book(self, book_id: str, local: bool, back_route):
        context = self.active_playback
        if context is not None and context.book.id == book_id and context.local == local:
            context.back_route = back_route
            self.player.play()
            context.last_sync_at = time.monotonic()
            context.was_playing = True
            return context

        await self.close_active_playback(suppress_errors=True)
        if local:
            book = DownloadStore().load(book_id)
            fallback = CONFIG.get("local_positions", {}).get(book_id, 0)
            start_time = fallback
            if self.api is not None:
                try:
                    start_time = await self.api.get_media_progress(book_id)
                except Exception:
                    start_time = fallback
            context = PlaybackContext(book=book, local=True, back_route=back_route)
        else:
            if self.api is None:
                raise RuntimeError("Audiobookshelf is unavailable while offline")
            session = await self.api.start_playback(book_id)
            book = session.book
            start_time = session.current_time
            context = PlaybackContext(
                book=book, local=False, session_id=session.id,
                back_route=back_route,
            )
        try:
            self.player.load(book.tracks, book.chapters, start_time)
            self.player.play()
            speeds = CONFIG.get("playback_speeds", {})
            self.player.rate = speeds.get(
                book.id, CONFIG.get("default_playback_speed", 1.0)
            )
        except Exception:
            if context.session_id:
                try:
                    await self.api.close_session(context.session_id, start_time, book.duration)
                except Exception:
                    logging.exception("Failed to close unusable audiobook session")
            raise
        context.last_sync_position = start_time
        context.last_sync_at = time.monotonic()
        context.was_playing = True
        self.active_playback = context
        CONFIG["current_book"] = {"book_id": book.id, "title": book.title, "local": local}
        CONFIG.sync()
        return context

    def persist_playback_speed(self, book_id: str, speed: float):
        speeds = dict(CONFIG.get("playback_speeds", {}))
        speeds[book_id] = round(float(speed), 2)
        CONFIG["playback_speeds"] = speeds
        CONFIG.sync()

    async def sync_active_playback(self, suppress_errors=False):
        context = self.active_playback
        if context is None:
            return
        position = self.player.position
        duration = context.book.duration or self.player.duration
        now = time.monotonic()
        if context.was_playing:
            context.pending_listened += max(0.0, now - context.last_sync_at)
        listened = context.pending_listened
        context.last_sync_at = now
        context.was_playing = self.player.is_playing
        if context.local:
            positions = dict(CONFIG.get("local_positions", {}))
            positions[context.book.id] = position
            CONFIG["local_positions"] = positions
            CONFIG.sync()
        if self.api is None:
            return
        try:
            if context.local:
                await self.api.update_media_progress(
                    context.book.id, position, duration,
                    finished=bool(duration and position >= duration - 1),
                )
            elif context.session_id:
                await self.api.sync_session(context.session_id, position, duration, listened)
            context.last_sync_position = position
            context.pending_listened = 0.0
        except Exception:
            if not suppress_errors:
                raise
            logging.exception("Failed to sync audiobook progress")

    async def pause_active_playback(self):
        if self.active_playback is None:
            return
        self.player.pause()
        await self.sync_active_playback(suppress_errors=True)

    async def close_active_playback(self, suppress_errors=False):
        context = self.active_playback
        if context is None:
            return
        await self.pause_active_playback()
        if context.session_id:
            try:
                await self.api.close_session(
                    context.session_id,
                    self.player.position,
                    context.book.duration or self.player.duration,
                )
            except Exception:
                if not suppress_errors:
                    raise
                logging.exception("Failed to close audiobook playback session")
        self.player.stop()
        self.active_playback = None

    async def run(self):
        await self.current_page.on_enter()
        await self.screen.listen()

    async def shutdown(self):
        CONFIG.sync()
        if self._inactivity_task and not self._inactivity_task.done():
            self._inactivity_task.cancel()
        page = self.current_page
        if isinstance(page, ScreensaverPage):
            page = page.previous_page
        await page.on_exit()
        await self.close_active_playback(suppress_errors=True)
        self.player.close()
