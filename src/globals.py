from PIL import ImageFont
import os
from pathlib import Path

DEBUG = os.uname().nodename == 'zeke'
ASSETS = Path("../assets").resolve()

WIDTH = 240
HEIGHT = 240

print(str((ASSETS / "Orbitron-VariableFont_wght.ttf").absolute()))

_FONT_SIZE = 24
THEME = {
    "font": ImageFont.truetype(str((ASSETS / "Orbitron-VariableFont_wght.ttf").absolute()), size=_FONT_SIZE),
    "text_size": _FONT_SIZE,
    "text_color": "#3C2B23",
    "bg": "#FFEFD7"
}

