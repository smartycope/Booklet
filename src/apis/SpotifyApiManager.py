import requests
import json
import argparse
import os
from src.constants import KEYS, SPOTIFY_API_BASE, CONFIG, TODO
from src.apis.ApiManager import ApiManager
import logging
logging.basicConfig(level=logging.INFO)

# TODO: use spotifywebapipython instead:
# https://pypi.org/project/spotifywebapipython/

# By hand version (untested)
class SpotifyApiManager(ApiManager):
    def __init__(self):
        super().__init__(SPOTIFY_API_BASE)
        self._playlists = None

    @property
    def liked_songs_playlist_id(self):
        raise TODO('are liked songs a playlist?')

    @property
    def playlists(self):
        if self._playlists is None:
            self._playlists = self.get_playlists()
        return self._playlists

    def get_playlists(self):
        self._playlists = [{'name': 'test', 'id': 'test'}, {'name': 'test2', 'id': 'test2'}]
        return self._playlists
        self._playlists = []
        path = 'me/playlists'
        while True:
            response = self.make_request(path)
            logging.info("Found %d playlists", len(response['items']))
            self._playlists.extend(response['items'])
            if response['next'] is None:
                return self._playlists
            path = response['next'].split(self.base)[1]

    @property
    def headers(self):
        try:
            return {'Authorization': f'Bearer {CONFIG["spotify_access_token"]}'}
        except KeyError:
            self.refresh_token()
            return {'Authorization': f'Bearer {CONFIG["spotify_access_token"]}'}

    def refresh_token(self):
        """Refresh the Spotify access token."""
        logging.info("Refreshing access token...")
        url = "https://accounts.spotify.com/api/token"
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': KEYS['spotify_refresh_token'],
        }
        auth = (KEYS['spotify_client_id'], KEYS['spotify_client_secret'])

        response = requests.post(url, data=payload, auth=auth, timeout=self.timeout)

        if response.status_code == 200:
            new_access_token = response.json().get('access_token')
            with CONFIG:
                CONFIG['spotify_access_token'] = new_access_token
            logging.info("Access token refreshed successfully.")
        else:
            logging.error("Failed to refresh token: %s - %s", response.status_code, response.text)
            raise Exception("Unable to refresh access token.")

    def make_request(self, endpoint, method='GET', data=None, **kwargs):
        logging.info("Making %s request to %s", method, endpoint)

        url = self.base + endpoint
        response = requests.request(method, url, headers=self.headers, timeout=self.timeout, **kwargs)

        if response.status_code == 401:
            logging.info("Access token expired. Attempting to refresh...")
            self.refresh_token()
            # Retry the request with the refreshed token
            return self.make_request(endpoint, method, data, **kwargs)

        response.raise_for_status()
        if response.status_code in (200, 201, 204):
            return response.json() if response.content else None
        else:
            logging.info("Request to %s Failed with code %s", endpoint, response.status_code)
            return None

    def get_current_playing_track(self):
        response = self.make_request('me/player/currently-playing')
        if response and response.get('item'):
            return response['item']
        return None

    def check_if_track_is_liked(self, track_id):
        response = self.make_request('me/tracks/contains', ids=track_id)
        if response is not None and len(response) > 0:
            return response[0]
        return False

    def remove_track_from_liked(self, track_id):
        self.make_request('me/tracks', method='DELETE', data={"ids": [track_id]})

    def add_track_to_playlist(self, track_id, playlist_id):
        self.make_request(f'playlists/{playlist_id}/tracks', method='POST', data={"uris": [f"spotify:track:{track_id}"]})

    def like_track(self, track_id):
        """Add a track to the user's liked songs."""
        self.make_request('me/tracks', method='PUT', data={"ids": [track_id]})

    def remove_track_from_playlist(self, track_id, playlist_id):
        """Remove a track from the specified playlist."""
        self.make_request(f'playlists/{playlist_id}/tracks', method='DELETE', data={"tracks": [{"uri": f"spotify:track:{track_id}"}]})

    def like_current_track(self):
        # Get the current playing track
        current_track = self.get_current_playing_track()
        if not current_track:
            logging.info("No track is currently playing.")
            return

        track_id = current_track['id']
        track_name = current_track['name']
        logging.info("Currently playing track: %s", track_name)

        # Add the track to Liked Songs
        self.like_track(track_id)
        logging.info("Added %s to your Liked Songs.", track_name)

        self.remove_track_from_playlist(track_id, PLAYLIST_ID)
        logging.info("Removed %s from playlist %s.", track_name, PLAYLIST_ID)

    def unlike_current_track(self):
        # Get the current playing track
        current_track = self.get_current_playing_track()
        if not current_track:
            logging.info("No track is currently playing.")
            return

        track_id = current_track['id']
        track_name = current_track['name']
        logging.info("Currently playing track: %s", track_name)

        # Check if the track is liked
        if self.check_if_track_is_liked(track_id):
            logging.info("%s is in your Liked Songs.", track_name)

            # Remove from Liked Songs
            self.remove_track_from_liked(track_id)
            logging.info("Removed %s from your Liked Songs.", track_name)

            # Add to specified playlist
            self.add_track_to_playlist(track_id, PLAYLIST_ID)
            logging.info("Added %s to playlist %s.", track_name, PLAYLIST_ID)

        else:
            logging.info("%s is not in your Liked Songs, nothing to move.", track_name)

spotify_api_manager = SpotifyApiManager()

# Generated by ChatGPT: it doesn't work:
# from spotifywebapipython import Spotify
# from typing import List, Optional

# class SpotifyApiManager:
#     def __init__(self):
#         self.sp = Spotify(
#             client_id=KEYS["spotify_client_id"],
#             client_secret=KEYS["spotify_client_secret"],
#             refresh_token=KEYS["spotify_refresh_token"],
#         )
#         self._dump_playlist_id = None

#     def _get_dump_playlist_id(self) -> Optional[str]:
#         """Find the playlist named 'dump songs', cache the ID, return it."""
#         if self._dump_playlist_id:
#             return self._dump_playlist_id

#         playlists = self.sp.playlists.me()
#         for p in playlists.items:
#             if p.name.lower() == "dump songs":
#                 self._dump_playlist_id = p.id
#                 return p.id
#         return None

#     def list_playlists(self) -> List[str]:
#         """Return a list of playlist names (or return full objects if preferred)."""
#         playlists = self.sp.playlists.me()
#         return {p.name: p.id for p in playlists.items}

#     def play(self):
#         self.sp.player.playback_start_resume()

#     def pause(self):
#         self.sp.player.playback_pause()

#     def toggle_play_pause(self):
#         self.sp.player.playback_toggle_play_pause()

#     def next_song(self):
#         self.sp.player.playback_next()

#     def prev_song(self):
#         self.sp.player.playback_previous()

#     def get_current_song_info(self):
#         """Return (title, artist, album) or None if nothing is playing."""
#         data = self.sp.player.playback_get_current_track()
#         if not data or not data.item:
#             return None

#         track = data.item
#         title = track.name
#         artist = ", ".join([a.name for a in track.artists])
#         album = track.album.name

#         return {
#             "title": title,
#             "artist": artist,
#             "album": album,
#             "track_id": track.id,  # handy to keep
#         }

#     def like_current_song(self):
#         info = self.get_current_song_info()
#         if not info:
#             return False
#         self.sp.library.follow_tracks([info["track_id"]])
#         return True

#     def delete_and_dump_current_song(self):
#         """
#         Remove currently playing song from:
#         - liked songs (if it’s there)
#         - OR the playlist currently playing (requires playback context)
#         Then add it to the 'dump songs' playlist.
#         """
#         info = self.get_current_song_info()
#         if not info:
#             return False

#         track_id = info["track_id"]

#         # 1. Remove from liked songs (safe if not liked)
#         try:
#             self.sp.library.unfollow_tracks([track_id])
#         except Exception:
#             pass

#         # 2. Try removing from the current playlist if context exists
#         playback = self.sp.player.playback_get_current_track()
#         context = getattr(playback, "context", None)

#         if context and context.type == "playlist":
#             playlist_id = context.href.split("/")[-1]
#             try:
#                 self.sp.playlists.remove_items(playlist_id, [track_id])
#             except Exception:
#                 pass

#         # 3. Add to "dump songs"
#         dump_id = self._get_dump_playlist_id()
#         if dump_id:
#             self.sp.playlists.add_items(dump_id, [track_id])

#         return True

