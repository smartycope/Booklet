from src.pages.ListPage import ListPage
from src.pages.AudiobookshelfLandingPage import AudiobookshelfLandingPage

class LocalBooksPage(ListPage):
    async def __init__(self):
        await super().__init__(
            items=self.fetch_books(),
            scrollable=True,
            title="Downloaded Books"
        )

    def fetch_books(self):
        return ['test', 'books', 'hello', 'world']

    async def left_pressed(self):
        return 'AudiobookshelfLanding'
