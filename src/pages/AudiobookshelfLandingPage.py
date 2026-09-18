from src import CONFIG
from src.DownloadStore import DownloadStore
from src.pages.ListPage import ListPage

class AudiobookshelfLandingPage(ListPage):
    @staticmethod
    def _login_error_message(error: Exception | None) -> str:
        current = error
        while current is not None:
            if getattr(current, "status", None) == 530:
                return "Login failed: server may be down (530)"
            current = current.__cause__ or current.__context__
        return "Login failed: check server and API key"

    @staticmethod
    def _format_storage(size: int) -> str:
        value = float(size)
        units = ("bytes", "KB", "MB", "GB", "TB")
        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == "bytes":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024

    async def __init__(self):
        items = []
        online = self.manager.api is not None
        current = CONFIG.get("current_book")
        if current and (online or current.get("local", False)):
            items.append((
                f"Resume {current['title']}",
                ("Player", {
                    "book_id": current["book_id"],
                    "local": current.get("local", False),
                    "back_route": "AudiobookshelfLanding",
                }),
            ))
        if online:
            items.extend([
                ("Download a Book", ("SelectCloudBook", {"download": True})),
                ("Stream a Book", ("SelectCloudBook", {"download": False})),
            ])
        items.extend([
            ("Play Downloaded Book", ("SelectDownloadedBook", {"delete": False})),
            ("Delete Downloaded Book", ("SelectDownloadedBook", {"delete": True})),
        ])
        if not online:
            items.append((
                self._login_error_message(getattr(self.manager, "api_error", None)),
                None,
            ))
        try:
            free_space = self._format_storage(DownloadStore().available_bytes())
            storage_label = f"Free space: {free_space}"
        except OSError:
            storage_label = "Free space unavailable"
        items.append((storage_label, None))
        await super().__init__(
            items=items,
            scrollable=True,
            title=f"Audiobookshelf ({'Online' if online else 'Offline'})",
            text_size=13,
        )

    def item_selected(self, item):
        return item

    async def left_pressed(self):
        return 'Landing'

    async def right_pressed(self):
        return await self.center_pressed()
