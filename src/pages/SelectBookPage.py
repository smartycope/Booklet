from src.pages.ListPage import ListPage

# TODO: I'm probably gonna delete this
class SelectBookPage(ListPage):
    async def __init__(self, title='Select Book', prev_page:str='AudiobookshelfLanding'):
        await super().__init__(
            items=self.fetch_books(),
            scrollable=True,
            title=self.title,
        )

        self.prev_page = prev_page

    def fetch_books(self):
        return

    async def left_pressed(self):
        return self.prev_page
