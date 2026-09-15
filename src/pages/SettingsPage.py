from src.pages.ListPage import ListPage

class SettingsPage(ListPage):
    async def __init__(self):
        await super().__init__(
            items={
                'Brightness': 'Brightness',
                'Volume': 'Volume',
                'Bluetooth': 'Bluetooth',
            },
            scrollable=False,
            title="Settings",
        )

    def item_selected(self, item):
        return item

    async def left_pressed(self):
        return self.item_selected(self.item_map[self.selected_item])

    async def right_pressed(self):
        return 'Landing'
