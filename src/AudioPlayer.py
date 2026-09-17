from __future__ import annotations

from bisect import bisect_right
from typing import Any

from src.AudiobookModels import Chapter, Track


class AudioPlayer:
    """VLC-backed player exposing one continuous timeline across audio files."""

    def __init__(self, vlc_module=None):
        # This is for testing purposes
        if vlc_module is None:
            try:
                import vlc as vlc_module
            except ImportError as error:
                raise RuntimeError("python-vlc and VLC/libVLC are required for audiobook playback") from error
        self.vlc = vlc_module
        self.instance = self.vlc.Instance("--no-video", "--quiet")
        self._player = self.instance.media_player_new()
        self._tracks: list[Track] = []
        self._chapters: list[Chapter] = []
        self._track_index = 0
        self._loaded = False
        self._ending = False
        self._track_ended = False
        event_type = getattr(getattr(self.vlc, "EventType", None), "MediaPlayerEndReached", None)
        if event_type is not None:
            self._player.event_manager().event_attach(event_type, self._on_track_end)

    def load(self, tracks: list[Track], chapters: list[Chapter] | None = None, start_time=0.0):
        if not tracks:
            raise ValueError("The audiobook has no playable audio tracks")
        self.stop()
        self._tracks = self._normalize_offsets(tracks)
        self._chapters = sorted(chapters or [], key=lambda chapter: chapter.start)
        self._track_index = -1
        self._loaded = True
        self.seek(start_time, autoplay=False)

    @staticmethod
    def _normalize_offsets(tracks: list[Track]) -> list[Track]:
        offset = 0.0
        normalized = []
        for track in tracks:
            start = track.start_offset if track.start_offset > 0 or not normalized else offset
            normalized.append(
                Track(track.title, track.source, max(0.0, track.duration), start, track.mime_type)
            )
            offset = start + max(0.0, track.duration)
        return normalized

    def _set_track(self, index: int, local_time=0.0, autoplay=True):
        self._track_index = max(0, min(index, len(self._tracks) - 1))
        media = self.instance.media_new(self._tracks[self._track_index].source)
        if local_time > 0 and hasattr(media, "add_option"):
            media.add_option(f":start-time={local_time}")
        self._player.set_media(media)
        if autoplay:
            self._player.play()
        if local_time > 0:
            self._player.set_time(round(local_time * 1000))

    def play(self):
        if not self._loaded:
            return
        self._player.play()

    def pause(self):
        if self.is_playing:
            self._player.pause()

    def stop(self):
        self._player.stop()

    def close(self):
        self.stop()
        release = getattr(self._player, "release", None)
        if release:
            release()
        release = getattr(self.instance, "release", None)
        if release:
            release()

    def play_pause(self):
        self.pause() if self.is_playing else self.play()

    @property
    def is_playing(self) -> bool:
        return bool(self._player.is_playing())

    @property
    def state(self) -> str:
        if self.is_playing:
            return "Playing"
        state = str(self._player.get_state()).casefold()
        if "end" in state:
            return "Finished"
        if self._loaded:
            return "Paused"
        return "Stopped"

    @property
    def duration(self) -> float:
        if not self._tracks:
            return 0.0
        track = self._tracks[-1]
        return track.start_offset + track.duration

    @property
    def position(self) -> float:
        if not self._tracks:
            return 0.0
        if "end" in str(self._player.get_state()).casefold():
            track = self._tracks[self._track_index]
            return min(self.duration, track.start_offset + track.duration)
        milliseconds = self._player.get_time()
        local = max(0.0, milliseconds / 1000 if milliseconds >= 0 else 0.0)
        return min(self.duration, self._tracks[self._track_index].start_offset + local)

    def seek(self, position: float, autoplay: bool | None = None):
        if not self._tracks:
            return
        was_playing = self.is_playing if autoplay is None else autoplay
        position = min(max(0.0, float(position)), self.duration)
        starts = [track.start_offset for track in self._tracks]
        index = min(len(self._tracks) - 1, max(0, bisect_right(starts, position) - 1))
        local_time = position - self._tracks[index].start_offset
        if index == self._track_index and self._player.get_media() is not None:
            self._player.set_time(round(local_time * 1000))
            if was_playing:
                self._player.play()
        else:
            self._set_track(index, local_time, was_playing)

    def seek_relative(self, seconds: float):
        self.seek(self.position + seconds)

    @property
    def current_chapter(self) -> Chapter | None:
        if not self._chapters:
            return None
        starts = [chapter.start for chapter in self._chapters]
        return self._chapters[max(0, bisect_right(starts, self.position) - 1)]

    def next_chapter(self):
        for chapter in self._chapters:
            if chapter.start > self.position + 0.5:
                self.seek(chapter.start)
                return
        self.seek(self.duration)

    def previous_chapter(self):
        starts = [chapter.start for chapter in self._chapters]
        if not starts:
            self.seek(0)
            return
        index = max(0, bisect_right(starts, self.position) - 1)
        if self.position - starts[index] <= 3 and index > 0:
            index -= 1
        self.seek(starts[index])

    # Compatibility aliases for old page code.
    next = next_chapter
    prev = previous_chapter

    @property
    def volume(self) -> float:
        level = self._player.audio_get_volume()
        return max(0.0, min(1.0, level / 100 if level >= 0 else 0.5))

    @volume.setter
    def volume(self, level: float):
        self._player.audio_set_volume(round(max(0.0, min(1.0, float(level))) * 100))

    def volume_up(self):
        self.volume = self.volume + 0.1

    def volume_down(self):
        self.volume = self.volume - 0.1

    @property
    def rate(self) -> float:
        level = self._player.get_rate()
        return max(0.0, level)

    @rate.setter
    def rate(self, level: float):
        self._player.set_rate(max(0.01, level))

    def rate_up(self):
        self.rate = self.rate + 0.1

    def rate_down(self):
        self.rate = self.rate - 0.1

    def _on_track_end(self, _event: Any):
        # libVLC invokes callbacks on its own thread. Defer player mutation to
        # the asyncio/UI thread to avoid re-entering libVLC from the callback.
        self._track_ended = True

    def poll(self):
        ended = self._track_ended or "end" in str(self._player.get_state()).casefold()
        if not ended or self._ending:
            return
        self._track_ended = False
        self._ending = True
        try:
            if self._track_index + 1 < len(self._tracks):
                self._set_track(self._track_index + 1, autoplay=True)
        finally:
            self._ending = False
