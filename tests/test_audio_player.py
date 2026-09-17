from src.AudioPlayer import AudioPlayer
from src.AudiobookModels import Chapter, Track


class FakeMedia:
    def __init__(self, source):
        self.source = source
        self.options = []

    def add_option(self, option):
        self.options.append(option)


class FakeEvents:
    def event_attach(self, *_args):
        pass


class FakePlayer:
    def __init__(self):
        self.media = None
        self.time = 0
        self.playing = False
        self.volume = 50

    def event_manager(self): return FakeEvents()
    def set_media(self, media): self.media = media
    def get_media(self): return self.media
    def play(self): self.playing = True
    def pause(self): self.playing = False
    def stop(self): self.playing = False
    def is_playing(self): return self.playing
    def set_time(self, milliseconds): self.time = milliseconds
    def get_time(self): return self.time
    def get_state(self): return "Playing" if self.playing else "Paused"
    def audio_get_volume(self): return self.volume
    def audio_set_volume(self, volume): self.volume = volume
    def set_rate(self, rate): self.rate = rate
    def release(self): pass


class FakeInstance:
    def __init__(self, *_args):
        self.player = FakePlayer()

    def media_player_new(self): return self.player
    def media_new(self, source): return FakeMedia(source)
    def release(self): pass


class FakeVlc:
    class EventType:
        MediaPlayerEndReached = 1

    Instance = FakeInstance


def player():
    instance = AudioPlayer(FakeVlc)
    instance.load(
        [Track("one", "one.mp3", 60, 0), Track("two", "two.mp3", 40, 60)],
        [Chapter("First", 0, 30), Chapter("Second", 30, 75), Chapter("Third", 75, 100)],
    )
    instance.play()
    return instance


def test_seek_uses_continuous_timeline_across_tracks():
    audio = player()
    audio.seek(65)
    assert audio._track_index == 1
    assert audio._player.get_time() == 5000
    assert audio.position == 65


def test_chapter_navigation_and_volume_clamping():
    audio = player()
    audio.seek(36)
    audio.previous_chapter()
    assert audio.position == 30
    audio.next_chapter()
    assert audio.position == 75
    audio.volume = 2
    assert audio.volume == 1


def test_track_end_advances_to_next_source():
    audio = player()
    audio._on_track_end(None)
    audio.poll()
    assert audio._track_index == 1
    assert audio._player.media.source == "two.mp3"


def test_playback_rate_survives_track_changes():
    audio = player()
    audio.rate = 1.7
    audio.seek(65)
    assert audio.rate == 1.7
    assert audio._player.rate == 1.7
