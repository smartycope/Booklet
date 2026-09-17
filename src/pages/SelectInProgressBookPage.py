from src.pages.ListPage import ListPage

class SelectInProgressBookPage(ListPage):
    async def __init__(self):
        await super().__init__(
            items=await self.fetch_books(),
            scrollable=True,
            title="In Progress Books"
        )

    async def fetch_books(self):
        return [i.media.metadata.title for i in await self.manager.api.get_books(in_progress=True)]

    async def left_pressed(self):
        return 'AudiobookshelfLanding'
