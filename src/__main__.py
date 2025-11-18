from src.screens.BaseScreen import BaseScreen
from src.screens.Screen import Screen
from src.screens.SimulatedScreen import SimulatedScreen
from src.pages import pages, Page
import os

from src.GuiManager import GuiManager

from src.constants import DEBUG

if __name__ == "__main__":
    # This number was chosen by trial and error. For a different monitor,
    # you may need to adjust this number.
    # rescale = (75, 75)
    rescale = False
    screen = SimulatedScreen(rescale) if DEBUG else Screen()
    GuiManager(screen, pages, 'landing').run()
