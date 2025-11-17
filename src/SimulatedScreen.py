import time
import spidev
import logging
import numpy as np
from gpiozero import DigitalOutputDevice, Button, PWMOutputDevice
import atexit
import pygame

from gpiozero import Device, LED
from gpiozero.pins.mock import MockFactory
from BaseScreen import BaseScreen

class SimulatedScreen(BaseScreen):
    def __init__(self, rescale=False):
        Device.pin_factory = MockFactory()
        super().__init__()

        pygame.display.init()

        self.screen = pygame.display.set_mode(rescale or (self.width, self.height))
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
        self.rescale = rescale

    def close(self):
        pygame.quit()

    def reset(self):
        """ Reset the display """
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def show_image(self, image):
        """Set buffer to value of Python Imaging Library image.
            Write display buffer to physical display
        """
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError(f"Image must be same dimensions as display ({imwidth}x{imheight}, should be {self.width}x{self.height})")
        # img = np.asarray(image)
        # pix = np.zeros((self.width,self.height,2), dtype = np.uint8)
        # pix[..., 0] = np.add(np.bitwise_and(img[..., 0],0xF8), np.right_shift(img[..., 1], 5))
        # pix[..., 1] = np.add(np.bitwise_and(np.left_shift(img[..., 1], 3), 0xE0), np.right_shift(img[..., 2], 3))
        # # pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
        # # pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0),np.right_shift(img[...,[2]],3))
        # pix = pix.flatten().tolist()
        mode = image.mode
        size = image.size
        data = image.tobytes()

        pygame_img = pygame.image.fromstring(data, size, mode)
        if self.rescale:
            pygame_img = pygame.transform.scale(pygame_img, self.rescale)
        self.screen.blit(pygame_img, (0, 0))
        pygame.display.update()

    def listen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.gpio_key_up_pin.pin.drive_low()
                    elif event.key == pygame.K_DOWN:
                        self.gpio_key_down_pin.pin.drive_low()
                    elif event.key == pygame.K_LEFT:
                        self.gpio_key_left_pin.pin.drive_low()
                    elif event.key == pygame.K_RIGHT:
                        self.gpio_key_right_pin.pin.drive_low()
                    elif event.key == pygame.K_RETURN:
                        self.gpio_key_center_pin.pin.drive_low()
                    elif event.key == pygame.K_1:
                        self.gpio_key1_pin.pin.drive_low()
                    elif event.key == pygame.K_2:
                        self.gpio_key2_pin.pin.drive_low()
                    elif event.key == pygame.K_3:
                        self.gpio_key3_pin.pin.drive_low()
                    elif event.key == pygame.K_ESCAPE:
                        self.close()
                        exit(0)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.gpio_key_up_pin.pin.drive_high()
                    elif event.key == pygame.K_DOWN:
                        self.gpio_key_down_pin.pin.drive_high()
                    elif event.key == pygame.K_LEFT:
                        self.gpio_key_left_pin.pin.drive_high()
                    elif event.key == pygame.K_RIGHT:
                        self.gpio_key_right_pin.pin.drive_high()
                    elif event.key == pygame.K_RETURN:
                        self.gpio_key_center_pin.pin.drive_high()
                    elif event.key == pygame.K_1:
                        self.gpio_key1_pin.pin.drive_high()
                    elif event.key == pygame.K_2:
                        self.gpio_key2_pin.pin.drive_high()
                    elif event.key == pygame.K_3:
                        self.gpio_key3_pin.pin.drive_high()
