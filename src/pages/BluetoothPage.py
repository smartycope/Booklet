from src.pages.ListPage import ListPage
from src.constants import TODO

class BluetoothPage(ListPage):
    def __init__(self):
        super().__init__(
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

    def up_pressed(self):
        return 'landing'

