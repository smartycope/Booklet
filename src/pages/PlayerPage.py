import subprocess

from src.aobject import aobject
from src.pages.Page import Page
from aioaudiobookshelf.schema.library import LibraryItemMinifiedBook, LibraryItemExpandedBook

type Book = LibraryItemMinifiedBook | LibraryItemExpandedBook

class PlayerPage(Page, aobject):
    # id: str

    async def __init__(self, play:Book|None=None):
        super().__init__()

    # TODO: should this add a bookmark instead?
    async def center_held(self):
        return 'Landing'

    async def center_pressed(self):
        self.manager.player.play_pause()
        return True

    async def left_pressed(self):
        self.manager.player.prev()
        return True

    async def right_pressed(self):
        self.manager.player.next()
        return True

    async def up_pressed(self):
        self.manager.player.volume_up()
        return True

    async def down_pressed(self):
        self.manager.player.volume_down()
        return True
