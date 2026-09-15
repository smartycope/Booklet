from src.pages.ListPage import ListPage

class AudiobookshelfLandingPage(ListPage):
    async def __init__(self):
        await super().__init__(
            items={'Play local book': 'audiobookshelf local', 'Download book': 'audiobookshelf download'},
            scrollable=False,
            title="AudiobookShelf",
        )

    def item_selected(self, item):
        return item

    async def left_pressed(self):
        return 'Landing'
