from src.pages.LandingPage import LandingPage
from src.pages.ListPage import ListPage
from src import TODO

class BluetoothLandingPage(ListPage):
    async def __init__(self):
        await super().__init__(
            items=self.scan(),
            scrollable=True,
            title="Bluetooth"
        )

    def scan(self):
        return ['hello', 'world']

    def connect(self, device):
        raise TODO('connect to bluetooth device')

    def item_selected(self, item):
        return self.connect(item)

    async def right_pressed(self):
        return 'Settings'
