from src.pages.ListPage import ListPage


class SettingsPage(ListPage):
    def __init__(self):
        super().__init__(
            items={
                'Brightness': 'brightness',
                'Volume': 'volume',
                'Bluetooth': 'bluetooth',
            },
            scrollable=False,
            title="Settings",
            right_pressed='landing'
        )

    def item_selected(self, item):
        return item
