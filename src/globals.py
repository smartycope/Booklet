from PIL import ImageFont
import os

DEBUG = os.uname().nodename == 'zeke'
FONT = ImageFont.truetype("../assets/Orbitron-VariableFont_wght.ttf", size=24)

WIDTH = 240
HEIGHT = 240