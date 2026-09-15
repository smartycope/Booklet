from PIL import ImageFont

from src import ASSETS

def font(size):
    return ImageFont.truetype(str(ASSETS / "Orbitron-VariableFont_wght.ttf"), size=size)
