import subprocess

from src.pages.Page import Page
from src.players.AudioPlayer import AudioPlayer


class PlayerPage(Page):
    id: str
    player_cls: AudioPlayer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = self.player_cls()

    def center_held(self):
        return "landing"

    def center_pressed(self):
        self.player.play_pause()
        return True

    def left_pressed(self):
        self.player.prev()
        return True

    def right_pressed(self):
        self.player.next()
        return True

    def up_pressed(self):
        self.player.volume_up()
        return True

    def down_pressed(self):
        self.player.volume_down()
        return True
