import asyncio

from src.BluetoothManager import BluetoothDevice, BluetoothManager
from src.pages.BluetoothPage import BluetoothPage
from src.pages.Page import Page


DEVICE = BluetoothDevice(
    path="/org/bluez/hci0/dev_00_11_22_33_44_55",
    name="Headphones",
    address="00:11:22:33:44:55",
    paired=True,
    connected=True,
)


class FakeBluetooth:
    def __init__(self):
        self.calls = []

    async def adapter_powered(self):
        return True

    async def devices(self):
        return [DEVICE]

    async def disconnect(self, device):
        self.calls.append(("disconnect", device))

    async def forget(self, device):
        self.calls.append(("forget", device))


class FakeManager:
    def render(self):
        pass


def test_connected_device_opens_disconnect_and_forget_menu():
    bluetooth = FakeBluetooth()
    Page.manager = FakeManager()
    page = asyncio.run(BluetoothPage(bluetooth=bluetooth))

    assert page.title == "Connected Devices"
    asyncio.run(page.center_pressed())

    assert page.title == "Headphones"
    assert page.items == ["Disconnect", "Forget", "Back"]
    assert bluetooth.calls == []


def test_forget_action_uses_manager_and_returns_to_device_list():
    bluetooth = FakeBluetooth()
    Page.manager = FakeManager()
    page = asyncio.run(BluetoothPage(bluetooth=bluetooth))
    asyncio.run(page.center_pressed())
    page._select_index(page.items.index("Forget"))

    asyncio.run(page.center_pressed())

    assert bluetooth.calls == [("forget", DEVICE)]
    assert page.title == "Connected Devices"


def test_manager_disconnects_connected_device_before_forgetting():
    calls = []

    class Interface:
        async def call_remove_device(self, path):
            calls.append(("remove", path))

    class Manager(BluetoothManager):
        async def disconnect(self, device):
            calls.append(("disconnect", device.path))

        async def _interface(self, path, interface_name):
            calls.append(("interface", path, interface_name))
            return Interface()

    manager = Manager()
    manager.adapter_path = "/org/bluez/hci0"

    asyncio.run(manager.forget(DEVICE))

    assert calls[0] == ("disconnect", DEVICE.path)
    assert calls[-1] == ("remove", DEVICE.path)
