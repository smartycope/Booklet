from src.pages.ListPage import ListPage
from src.apis.SpotifyApiManager import spotify_api_manager

class SpotifyPlaylistPage(ListPage):
    def __init__(self):
        super().__init__(
            items={p['name']: p['id'] for p in spotify_api_manager.playlists},
            scrollable=True,
            title="Spotify Playlists"
        )

    def right_pressed(self):
        return 'landing'

    def item_selected(self, item):
        return 'spotify player', item
