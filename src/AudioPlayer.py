import re
import subprocess


class AudioPlayer:
    def __init__(self):
        # self.volume = self.get_volume()
        self.volume_step = 0.1

    def play(self, path):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def next(self):
        pass

    def prev(self):
        pass

    @property
    def volume(self):
        match = re.search(r'\[\d+%\]',
            subprocess.run('amixer -D pulse sget Master'.split(),
                    check=True, capture_output=True, text=True).stdout
        )
        return int(match.group(0).strip('[]%')) if match else .5

    @volume.setter
    def volume(self, to):
        subprocess.run(f"amixer sset Master {to*100}%".split(" "), check=True)

    def volume_up(self):
        self.volume += self.volume_step
        # self.set_volume(self.volume)

    def volume_down(self):
        self.volume -= self.volume_step
        # self.set_volume(self.volume)

    # TODO: should this use the API instead?
    def play_pause(self):
        subprocess.run("mpc toggle".split(" "), check=True)
