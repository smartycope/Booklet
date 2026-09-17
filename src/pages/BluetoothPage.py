from src.BluetoothManager import BluetoothManager
from src.pages.ListPage import ListPage


_bluetooth = BluetoothManager()


class BluetoothPage(ListPage):
    async def __init__(self, bluetooth=None):
        self.bluetooth = bluetooth or _bluetooth
        self.show_discovered = False
        items = await self._items()
        await super().__init__(
            items=items,
            scrollable=True,
            title="Bluetooth",
            text_size=12,
        )

    async def _items(self):
        if not await self.bluetooth.adapter_powered():
            return {"Turn Bluetooth on": ("power_on", None)}

        devices = await self.bluetooth.devices()
        items = {}
        used_labels = set()
        for device in devices:
            if not (device.connected or device.paired or self.show_discovered):
                continue

            if device.connected:
                verb = "Disconnect"
                action = "disconnect"
            elif device.paired:
                verb = "Connect"
                action = "connect"
            else:
                verb = "Pair"
                action = "pair"

            label = f"{device.name}"
            self.title = f'Bluetooth - {verb}'
            if label in used_labels:
                label = f"{label} ({device.address[-5:]})"
            used_labels.add(label)
            items[label] = (action, device)

        items["Scan for devices"] = ("scan", None)
        return items

    def _show_status(self, status):
        self.title = status
        self._draw_items()
        if getattr(self, "manager", None) is not None:
            self.manager.render()

    async def _refresh(self):
        selected_item = self.selected_item
        self.item_map = await self._items()
        self.entries = list(self.item_map.items())
        self.items = [label for label, _value in self.entries]
        self.selected_index = (
            self.items.index(selected_item) if selected_item in self.items else 0
        )
        self.title = "Bluetooth"
        self._draw_items()

    async def item_selected(self, item):
        action, device = item
        if action == "scan":
            self._show_status("Scanning...")
            await self.bluetooth.discover()
            self.show_discovered = True
        elif action == "power_on":
            self._show_status("Turning on...")
            await self.bluetooth.power_on()
        elif action == "pair":
            self._show_status("Pairing...")
            await self.bluetooth.pair_and_connect(device)
            self.show_discovered = False
        elif action == "connect":
            self._show_status("Connecting...")
            await self.bluetooth.connect(device)
        elif action == "disconnect":
            self._show_status("Disconnecting...")
            await self.bluetooth.disconnect(device)

        await self._refresh()
        return True

    async def center_pressed(self):
        if not self.items:
            return None
        return await self.item_selected(self.selected_value)

    async def right_pressed(self):
        return 'Settings'
