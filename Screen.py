import time
import spidev
import logging
import numpy as np
from gpiozero import DigitalOutputDevice, DigitalInputDevice, PWMOutputDevice

class Screen:
    #GPIO define
    KEY_UP_PIN    = 6
    KEY_DOWN_PIN  = 19
    KEY_LEFT_PIN  = 5
    KEY_RIGHT_PIN = 26
    KEY_PRESS_PIN = 13

    KEY1_PIN      = 21
    KEY2_PIN      = 20
    KEY3_PIN      = 16

    width  = 240
    height = 240

    def __init__(self,
        clear=True,
        brightness=1,
        spi=spidev.SpiDev(0,0),
        spi_freq=40000000,
        rst = 27,
        dc = 25,
        bl = 24,
        bl_freq=1000,
        # i2c=None,
        # i2c_freq=100000
    ):
        self.spi_freq = spi_freq
        self.bl_freq = bl_freq

        self.gpio_rst_pin= DigitalOutputDevice(rst, active_high=True, initial_value=False)
        self.gpio_dc_pin = DigitalOutputDevice(dc, active_high=True, initial_value=False)
        self.gpio_bl_pin = PWMOutputDevice(bl, frequency=self.bl_freq)

        self.gpio_key_up_pin    = DigitalInputDevice(self.KEY_UP_PIN, pull_up=True, active_state=None)
        self.gpio_key_down_pin  = DigitalInputDevice(self.KEY_DOWN_PIN, pull_up=True, active_state=None)
        self.gpio_key_left_pin  = DigitalInputDevice(self.KEY_LEFT_PIN, pull_up=True, active_state=None)
        self.gpio_key_right_pin = DigitalInputDevice(self.KEY_RIGHT_PIN, pull_up=True, active_state=None)
        self.gpio_key_press_pin = DigitalInputDevice(self.KEY_PRESS_PIN, pull_up=True, active_state=None)

        self.gpio_key1_pin      = DigitalInputDevice(self.KEY1_PIN, pull_up=True, active_state=None)
        self.gpio_key2_pin      = DigitalInputDevice(self.KEY2_PIN, pull_up=True, active_state=None)
        self.gpio_key3_pin      = DigitalInputDevice(self.KEY3_PIN, pull_up=True, active_state=None)

        #Initialize SPI
        self.spi = spi
        self.spi.max_speed_hz = spi_freq
        self.spi.mode = 0b00

        self.init_display()

        self._brightness = 0
        self.brightness = brightness

        if clear:
            self.clear()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        self.gpio_bl_pin.value = value / 2

    def close(self):
        logging.debug("spi end")
        # if self.spi is not None:
        self.spi.close()

        logging.debug("gpio cleanup...")
        self.gpio_rst_pin.on()
        self.gpio_dc_pin.off()
        self.gpio_bl_pin.close()
        time.sleep(0.001)

    def send_command(self, cmd):
        self.gpio_dc_pin.off()
        self.spi.writebytes([cmd])

    def send_data(self, val):
        self.gpio_dc_pin.on()
        self.spi.writebytes([val])

    def reset(self):
        """ Reset the display """
        self.gpio_rst_pin.on()
        time.sleep(0.01)
        self.gpio_rst_pin.off()
        time.sleep(0.01)
        self.gpio_rst_pin.on()
        time.sleep(0.01)

    def init_display(self):
        """Initialize dispaly"""
        self.reset()

        self.send_command(0x36)
        self.send_data(0x70)                 #self.data(0x00)

        self.send_command(0x11)

        time.sleep(0.12)

        self.send_command(0x36)
        self.send_data(0x00)

        self.send_command(0x3A)
        self.send_data(0x05)

        self.send_command(0xB2)
        self.send_data(0x0C)
        self.send_data(0x0C)
        self.send_data(0x00)
        self.send_data(0x33)
        self.send_data(0x33)

        self.send_command(0xB7)
        self.send_data(0x00)

        self.send_command(0xBB)
        self.send_data(0x3F)

        self.send_command(0xC0)
        self.send_data(0x2C)

        self.send_command(0xC2)
        self.send_data(0x01)

        self.send_command(0xC3)
        self.send_data(0x0D)

        self.send_command(0xC6)
        self.send_data(0x0F)

        self.send_command(0xD0)
        self.send_data(0xA7)

        self.send_command(0xD0)
        self.send_data(0xA4)
        self.send_data(0xA1)

        self.send_command(0xD6)
        self.send_data(0xA1)

        self.send_command(0xE0)
        self.send_data(0xF0)
        self.send_data(0x00)
        self.send_data(0x02)
        self.send_data(0x01)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x27)
        self.send_data(0x43)
        self.send_data(0x3F)
        self.send_data(0x33)
        self.send_data(0x0E)
        self.send_data(0x0E)
        self.send_data(0x26)
        self.send_data(0x2E)

        self.send_command(0xE1)
        self.send_data(0xF0)
        self.send_data(0x07)
        self.send_data(0x0D)
        self.send_data(0x0D)
        self.send_data(0x0B)
        self.send_data(0x16)
        self.send_data(0x26)
        self.send_data(0x43)
        self.send_data(0x3E)
        self.send_data(0x3F)
        self.send_data(0x19)
        self.send_data(0x19)
        self.send_data(0x31)
        self.send_data(0x3A)

        self.send_command(0x21)

        self.send_command(0x29)

    def set_windows(self, x_start, y_start, x_end, y_end):
        #set the X coordinates
        self.send_command(0x2A)
        self.send_data(0x00)               #Set the horizontal starting point to the high octet
        self.send_data(x_start & 0xff)     #Set the horizontal starting point to the low octet
        self.send_data(0x00)               #Set the horizontal end to the high octet
        self.send_data((x_end - 1) & 0xff) #Set the horizontal end to the low octet

        #set the Y coordinates
        self.send_command(0x2B)
        self.send_data(0x00)
        self.send_data((y_start & 0xff))
        self.send_data(0x00)
        self.send_data((y_end - 1) & 0xff )

        self.send_command(0x2C)

    def show_image(self, image):
        """Set buffer to value of Python Imaging Library image.
            Write display buffer to physical display
        """
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError(f"Image must be same dimensions as display ({imwidth}x{imheight}, should be {self.width}x{self.height})")
        img = np.asarray(image)
        pix = np.zeros((self.width,self.height,2), dtype = np.uint8)
        pix[..., 0] = np.add(np.bitwise_and(img[..., 0],0xF8), np.right_shift(img[..., 1], 5))
        pix[..., 1] = np.add(np.bitwise_and(np.left_shift(img[..., 1], 3), 0xE0), np.right_shift(img[..., 2], 3))
        # pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
        # pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0),np.right_shift(img[...,[2]],3))
        pix = pix.flatten().tolist()
        self.set_windows(0, 0, self.width, self.height)
        self.gpio_dc_pin.on()
        for i in range(0, len(pix), 4096):
            self.spi.writebytes(pix[i:i+4096])

    def clear(self):
        """Clear contents of image buffer"""
        _buffer = [0xff] * (self.width * self.height * 2)
        self.set_windows(0, 0, self.width, self.height)
        self.gpio_dc_pin.on()
        for i in range(0, len(_buffer), 4096):
            self.spi.writebytes(_buffer[i:i+4096])


