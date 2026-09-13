from src.pages.ListPage import ListPage

class AudiobookShelfDownloadPage(ListPage):
    def __init__(self):
        super().__init__(
            items=self.fetch_books(),
            scrollable=True,
            title="Select Book to Download",
            left_pressed='audiobookshelf landing'
        )

    def fetch_books(self):
        return ['test', 'books', 'hello', 'world']
