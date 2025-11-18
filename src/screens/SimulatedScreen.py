import atexit
import logging
import time

import numpy as np
import spidev
from gpiozero import LED, Button, Device, DigitalOutputDevice, PWMOutputDevice
from gpiozero.pins.mock import MockFactory

from src.constants import DEBUG
from src.screens.BaseScreen import BaseScreen

# The pi doesn't have pygame, nor should it
if DEBUG:
    import pygame

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

    def show_image(self, image, x_start=0, y_start=0, x_end=None, y_end=None):
        """Set buffer to value of Python Imaging Library image.
            Write display buffer to physical display
        """
        x_end = x_end or self.width
        y_end = y_end or self.height

        imwidth, imheight = image.size
        if imwidth != x_end - x_start or imheight != y_end - y_start:
            # raise ValueError(f"Image must be same dimensions as display ({imwidth}x{imheight}, should be {self.width}x{self.height})")
            image = image.crop((x_start, y_start, x_end, y_end))

        mode = image.mode
        size = image.size
        data = image.tobytes()

        pygame_img = pygame.image.fromstring(data, size, mode)
        if self.rescale:
            pygame_img = pygame.transform.scale(pygame_img, self.rescale)
        self.screen.blit(pygame_img, (x_start, y_start))
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
