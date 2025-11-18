from .Page import Page
from .StaticPage import StaticPage
# from .ListPage import ListPage
# from .PlayerPage import PlayerPage

from src.pages.LandingPage import LandingPage
from src.pages.ListPage import ListPage
from src.pages.AudiobookShelfLocalPage import AudiobookShelfLocalPage
from src.pages.AudiobookShelfDownloadPage import AudiobookShelfDownloadPage
from src.pages.SpotifyPlaylistPage import SpotifyPlaylistPage
from src.pages.SpotifyPlayerPage import SpotifyPlayerPage
from src.pages.SettingsPage import SettingsPage
from src.pages.AudiobookShelfLandingPage import AudiobookShelfLandingPage

pages = {
    "landing": LandingPage(),

    "spotify playlist": SpotifyPlaylistPage(),

    "audiobookshelf landing": AudiobookShelfLandingPage(),
    "audiobookshelf local": AudiobookShelfLocalPage(),
    "audiobookshelf download": AudiobookShelfDownloadPage(),

    "settings": SettingsPage(),

    "spotify player": SpotifyPlayerPage(),
}

