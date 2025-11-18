from src.pages.ListPage import ListPage


class AudiobookShelfLandingPage(ListPage):
    def __init__(self):
        super().__init__(
            items={'Play local book': 'audiobookshelf local', 'Download book': 'audiobookshelf download'},
            scrollable=False,
            title="AudiobookShelf"
        )

    def left_pressed(self):
        return 'landing'

    def item_selected(self, item):
        return item

