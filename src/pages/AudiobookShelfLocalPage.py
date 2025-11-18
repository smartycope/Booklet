from src.pages.ListPage import ListPage

class AudiobookShelfLocalPage(ListPage):
    def __init__(self):
        super().__init__(
            items=self.fetch_books(),
            scrollable=True,
            title="Downloaded Books"
        )

    def fetch_books(self):
        return ['test', 'books', 'hello', 'world']

    def left_pressed(self):
        return 'audiobookshelf landing'
