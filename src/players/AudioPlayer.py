from abc import ABC, abstractmethod
import subprocess


class AudioPlayer(ABC):
    """ An audio player. Not necissary since we removed Spotify support, but it might be useful in
        the future.
    """

    volume = 0.5

    def __init__(self):
        pass

    @abstractmethod
    def play(self, path):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def prev(self):
        pass

    def set_volume(self, to):
        subprocess.run(f"amixer sset Master {to*100}%".split(" "), check=True)

    def volume_up(self):
        AudioPlayer.volume += 0.1
        self.set_volume(AudioPlayer.volume)

    def volume_down(self):
        AudioPlayer.volume -= 0.1
        self.set_volume(AudioPlayer.volume)

    def play_pause(self):
        subprocess.run(f"mpc toggle".split(" "), check=True)
