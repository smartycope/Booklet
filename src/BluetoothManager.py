import asyncio
from dataclasses import dataclass

from dbus_next import BusType
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method


BLUEZ_SERVICE = "org.bluez"
ADAPTER_INTERFACE = "org.bluez.Adapter1"
DEVICE_INTERFACE = "org.bluez.Device1"
OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
AGENT_MANAGER_INTERFACE = "org.bluez.AgentManager1"
AGENT_PATH = "/com/booklet/bluetooth_agent"


@dataclass(frozen=True, slots=True)
class BluetoothDevice:
    path: str
    name: str
    address: str
    paired: bool
    connected: bool
    rssi: int | None = None


class PairingAgent(ServiceInterface):
    """A headless BlueZ agent suitable for speakers and headphones."""

    def __init__(self):
        super().__init__("org.bluez.Agent1")

    @method()
    def Release(self):
        pass

    @method()
    def RequestPinCode(self, device: "o") -> "s":
        return "0000"

    @method()
    def DisplayPinCode(self, device: "o", pincode: "s"):
        pass

    @method()
    def RequestPasskey(self, device: "o") -> "u":
        return 0

    @method()
    def DisplayPasskey(self, device: "o", passkey: "u", entered: "q"):
        pass

    @method()
    def RequestConfirmation(self, device: "o", passkey: "u"):
        pass

    @method()
    def RequestAuthorization(self, device: "o"):
        pass

    @method()
    def AuthorizeService(self, device: "o", uuid: "s"):
        pass

    @method()
    def Cancel(self):
        pass


class BluetoothManager:
    """Small async wrapper around the BlueZ D-Bus API."""

    def __init__(self, discovery_seconds=8):
        self.discovery_seconds = discovery_seconds
        self.bus = None
        self.adapter_path = None
        self._agent = None
        self._agent_registered = False

    async def _connect(self):
        if self.bus is not None and self.bus.connected:
            return

        self._agent = None
        self._agent_registered = False
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        managed_objects = await self._managed_objects()
        self.adapter_path = next(
            (
                path
                for path, interfaces in managed_objects.items()
                if ADAPTER_INTERFACE in interfaces
            ),
            None,
        )
        if self.adapter_path is None:
            raise RuntimeError("No Bluetooth adapter was found")

    async def _managed_objects(self):
        if self.bus is None:
            raise RuntimeError("Bluetooth is not initialized")
        introspection = await self.bus.introspect(BLUEZ_SERVICE, "/")
        proxy = self.bus.get_proxy_object(BLUEZ_SERVICE, "/", introspection)
        manager = proxy.get_interface(OBJECT_MANAGER_INTERFACE)
        return await manager.call_get_managed_objects()

    async def _interface(self, path, interface_name):
        await self._connect()
        introspection = await self.bus.introspect(BLUEZ_SERVICE, path)
        proxy = self.bus.get_proxy_object(BLUEZ_SERVICE, path, introspection)
        return proxy.get_interface(interface_name)

    @staticmethod
    def _value(properties, name, default=None):
        variant = properties.get(name)
        return default if variant is None else variant.value

    async def adapter_powered(self):
        await self._connect()
        adapter = await self._interface(self.adapter_path, ADAPTER_INTERFACE)
        return await adapter.get_powered()

    async def power_on(self):
        await self._connect()
        adapter = await self._interface(self.adapter_path, ADAPTER_INTERFACE)
        await adapter.set_powered(True)

    async def devices(self):
        await self._connect()
        managed_objects = await self._managed_objects()
        devices = []
        for path, interfaces in managed_objects.items():
            properties = interfaces.get(DEVICE_INTERFACE)
            if properties is None:
                continue

            address = self._value(properties, "Address", "Unknown")
            name = (
                self._value(properties, "Alias")
                or self._value(properties, "Name")
                or address
            )
            devices.append(
                BluetoothDevice(
                    path=path,
                    name=name,
                    address=address,
                    paired=self._value(properties, "Paired", False),
                    connected=self._value(properties, "Connected", False),
                    rssi=self._value(properties, "RSSI"),
                )
            )

        return sorted(
            devices,
            key=lambda device: (
                not device.connected,
                not device.paired,
                -(device.rssi if device.rssi is not None else -999),
                device.name.casefold(),
            ),
        )

    async def discover(self):
        await self._connect()
        adapter = await self._interface(self.adapter_path, ADAPTER_INTERFACE)
        started = False
        try:
            await adapter.call_start_discovery()
            started = True
            await asyncio.sleep(self.discovery_seconds)
        finally:
            if started:
                await adapter.call_stop_discovery()
        return await self.devices()

    async def _register_agent(self):
        if self._agent_registered:
            return

        await self._connect()
        self._agent = PairingAgent()
        self.bus.export(AGENT_PATH, self._agent)
        manager = await self._interface("/org/bluez", AGENT_MANAGER_INTERFACE)
        try:
            await manager.call_register_agent(AGENT_PATH, "NoInputNoOutput")
        except Exception:
            self.bus.unexport(AGENT_PATH, self._agent)
            self._agent = None
            raise
        self._agent_registered = True

    async def pair_and_connect(self, device):
        await self._register_agent()
        interface = await self._interface(device.path, DEVICE_INTERFACE)
        if not device.paired:
            await interface.call_pair()
            await interface.set_trusted(True)
            device = next(
                current
                for current in await self.devices()
                if current.path == device.path
            )
        if not device.connected:
            await interface.call_connect()

    async def connect(self, device):
        interface = await self._interface(device.path, DEVICE_INTERFACE)
        await interface.call_connect()

    async def disconnect(self, device):
        interface = await self._interface(device.path, DEVICE_INTERFACE)
        await interface.call_disconnect()

    async def forget(self, device):
        if device.connected:
            await self.disconnect(device)
        adapter = await self._interface(self.adapter_path, ADAPTER_INTERFACE)
        await adapter.call_remove_device(device.path)
