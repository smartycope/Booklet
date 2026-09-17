from src import CONFIG
from src.pages.ListPage import ListPage

class AudiobookshelfLandingPage(ListPage):
    async def __init__(self):
        items = []
        current = CONFIG.get("current_book")
        if current:
            items.append((
                f"Resume {current['title']}",
                ("Player", {
                    "book_id": current["book_id"],
                    "local": current.get("local", False),
                    "back_route": "AudiobookshelfLanding",
                }),
            ))
        items.extend([
            ("Download a Book", ("SelectCloudBook", {"download": True})),
            ("Stream a Book", ("SelectCloudBook", {"download": False})),
            ("Play Downloaded Book", ("SelectDownloadedBook", {"delete": False})),
            ("Delete Downloaded Book", ("SelectDownloadedBook", {"delete": True})),
        ])
        await super().__init__(
            items=items,
            scrollable=True,
            title="Audiobookshelf",
            text_size=13,
        )

    def item_selected(self, item):
        return item

    async def left_pressed(self):
        return 'Landing'
