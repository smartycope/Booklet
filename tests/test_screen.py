import importlib

import pytest

screen_module = importlib.import_module("src.screens.Screen")


def test_missing_spi_device_has_actionable_error(monkeypatch):
    def missing_device(_bus, _device):
        raise FileNotFoundError(2, "No such file or directory")

    monkeypatch.setattr(screen_module.spidev, "SpiDev", missing_device)

    with pytest.raises(RuntimeError) as error:
        screen_module.Screen._open_spi()

    message = str(error.value)
    assert "/dev/spidev0.0" in message
    assert "sudo raspi-config nonint do_spi 0" in message
