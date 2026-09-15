import asyncio
from functools import partial
import logging
from src import pages
from src.pages.ErrorPage import ErrorPage
from src.pages.Page import Page
from src.AudioPlayer import AudioPlayer
from src.AudiobookshelfApiManager import AudiobookshelfApiManager
from src.screens.BaseScreen import BaseScreen

from src.pages.AudiobookshelfLandingPage import AudiobookshelfLandingPage
from src.pages.BluetoothLandingPage import BluetoothPage
from src.pages.LandingPage import LandingPage
from src.pages.LocalBooksPage import LocalBooksPage
from src.pages.SelectBookPage import SelectBookPage
from src.pages.SettingsPage import SettingsPage
from src.pages.StaticTextPage import StaticTextPage
from src.pages.VolumePage import VolumePage
from src.pages.BrightnessPage import BrightnessPage
from src.pages.PlayerPage import PlayerPage
from src.pages.Page import Page

class GuiManager:
    """ Manage the connection between the screen and the pages. Handles events, and switches between pages. """
    def __init__(self, player:AudioPlayer, api:AudiobookshelfApiManager, screen:BaseScreen, first_page:Page):
        self.player = player
        self.api = api
        self.screen = screen
        self.pages = pages

        self.current_page = first_page
        # self.goto_page(first_page)

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


    def dispatch_event(self, device, event=None):
        future = asyncio.run_coroutine_threadsafe(
            self.handle_event(device, event),
            self.loop,
        )
        future.add_done_callback(self._event_finished)

    # @staticmethod
    def _event_finished(self, future):
        exception = future.exception()
        if exception is not None:
            self.current_page = ErrorPage(exception)
            logging.exception(
                "Button event failed",
                exc_info=(type(exception), exception, exception.__traceback__),
            )

    async def handle_event(self, device, event=None):
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
        # if isinstance(rtn, Page):
            # self.goto_page(rtn)
            # if isinstance(page, str):
            self.current_page = await self.page(rtn)
        elif isinstance(rtn, tuple):
            # If the handler returns a tuple of a string and a dictionary, goto that page, and set those
            # attributes on the page class
            if type(rtn[0]) is str and type(rtn[1]) is dict:
            #     self.goto_page(rtn[0], rtn[1])
                self.current_page = await self.page(rtn[0], **rtn[1])
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

    # async def goto_page(self, page:Page|str):
    #     if isinstance(page, str):
    #         page = await self.page(page)
    #     # self.current_page_name = page.__class__.__name__
    #     self._current_page = page
    #     self.render()

    @current_page.setter
    def current_page(self, page:Page):
        # if isinstance(page, str):
        #     page = await self.page(page)
        # self.current_page_name = page.__class__.__name__
        self._current_page = page
        self.render()

    # def goto_page(self, name:str, data:dict={}):
    #     if isinstance(name, str):
    #         if name in pages:
    #             self.current_page_name = name
    #             for k, v in data.items():
    #                 setattr(self.current_page.__class__, k, v)
    #             self.render()
    #         else:
    #             raise ValueError(f"Page with name {name} does not exist")
    #     else:
    #         raise ValueError(f"Page name must be a string, not {type(name)}")

    # def run(self):
    #     self.screen.listen()
    # GuiManager.py

    async def run(self):
        await self.screen.listen()
