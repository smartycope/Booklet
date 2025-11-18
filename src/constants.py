from PIL import ImageFont
import os
from pathlib import Path
import shelve
import json

DEBUG = os.uname().nodename == 'zeke'
ASSETS = (Path(__file__).parent.parent / "assets").absolute()

WIDTH = 240
HEIGHT = 240

_FONT_SIZE = 16
THEME = {
    "font": ImageFont.truetype(str((ASSETS / "Orbitron-VariableFont_wght.ttf")), size=_FONT_SIZE),
    "text_size": _FONT_SIZE,
    "text_color": "#3C2B23",
    "bg": "#FFEFD7",
    "radius": 5
}

# For things which are generated, but we want preserved
C = CONFIG = shelve.open("booklet")

if DEBUG:
    _EXTERNAL_CONFIG_PATH = Path(__file__).parent.parent / "booklet_config.json"
else:
    _EXTERNAL_CONFIG_PATH = Path.home() / "booklet_config.json"
# For things which are constant (per user), are read-only, and are sensitive
KEYS = json.loads(_EXTERNAL_CONFIG_PATH.read_text())

SPOTIFY_API_BASE = 'https://api.spotify.com/v1/'
AUDIOBOOKSHELF_API_BASE = KEYS["audiobookshelf_url"]

class TODO(NotImplementedError): pass
