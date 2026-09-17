from src import CONFIG
from src.pages.ListPage import ListPage
from collections import OrderedDict

class AudiobookshelfLandingPage(ListPage):
    async def __init__(self):
        items = OrderedDict({
            'Play local book': 'LocalBooks',
            # 'Download book': 'CloudBooks',
            'Download an In Progress Book': 'SelectInProgressBook',
        })

        if book := CONFIG.get('last_played_book'):
            items[f'Resume {book.media.metadata.title}'] = ('Player', {'play': book})
            items.move_to_end('Resume last book', last=False)

        await super().__init__(
            items=items,
            scrollable=False,
            title="Audiobookshelf",
        )

    def item_selected(self, item):
        return item

    async def left_pressed(self):
        return 'Landing'
