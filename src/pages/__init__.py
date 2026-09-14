from .Page import Page
from .StaticPage import StaticPage
# from .ListPage import ListPage
# from .PlayerPage import PlayerPage

from src.pages.LandingPage import LandingPage
from src.pages.ListPage import ListPage
from src.pages.AudiobookShelfLocalPage import AudiobookShelfLocalPage
from src.pages.AudiobookShelfDownloadPage import AudiobookShelfDownloadPage
# from old_code.SpotifyPlaylistPage import SpotifyPlaylistPage
# from old_code.SpotifyPlayerPage import SpotifyPlayerPage
from src.pages.SettingsPage import SettingsPage
from src.pages.AudiobookShelfLandingPage import AudiobookShelfLandingPage
from src.pages.BarLevelPage import BarLevelPage
from src.pages.VolumePage import VolumePage
from src.pages.BrightnessPage import BrightnessPage
from src.pages.BluetoothPage import BluetoothPage

pages = {
    "landing": LandingPage(),

    "audiobookshelf landing": AudiobookShelfLandingPage(),
    "audiobookshelf local": AudiobookShelfLocalPage(),
    "audiobookshelf download": AudiobookShelfDownloadPage(),

    "settings": SettingsPage(),
    "brightness": BrightnessPage(),
    "volume": VolumePage(),
    "bluetooth": BluetoothPage(),
}
