from Screen import Screen
from SimulatedScreen import SimulatedScreen
from BaseScreen import BaseScreen
from pages import pages, Page
import os

from GuiManager import GuiManager

from globals import DEBUG

if __name__ == "__main__":
    # This number was chosen by trial and error. For a different monitor,
    # you may need to adjust this number.
    # rescale = (75, 75)
    rescale = False
    screen = SimulatedScreen(rescale) if DEBUG else Screen()
    GuiManager(screen, pages, 'landing').run()
