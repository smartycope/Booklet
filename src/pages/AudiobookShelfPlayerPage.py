from src.pages.PlayerPage import PlayerPage
from src.players.AudiobookShelfPlayer import AudiobookShelfPlayer

class AudiobookShelfPlayerPage(PlayerPage):
    def __init__(self, id, **kwargs):
        super().__init__(cls=AudiobookShelfPlayer, id=id, **kwargs)