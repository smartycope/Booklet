from src.pages.ListPage import ListPage


class SettingsPage(ListPage):
    def __init__(self):
        super().__init__(
            items=['Brightness', 'Volume', 'Bluetooth'],
            scrollable=False,
            title="Settings",
            right_pressed='landing'
        )

    def item_selected(self, item):
        print(f"Selected item: {item}")
        # return item
