from src.pages.PlayerPage import PlayerPage
from old_code.SpotifyPlayer import SpotifyPlayer


class SpotifyPlayerPage(PlayerPage):
    id = 'spotify player'
    player_cls = SpotifyPlayer
