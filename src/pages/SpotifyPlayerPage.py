from src.pages.PlayerPage import PlayerPage
from src.players.SpotifyPlayer import SpotifyPlayer


class SpotifyPlayerPage(PlayerPage):
    id = 'spotify player'
    player_cls = SpotifyPlayer

