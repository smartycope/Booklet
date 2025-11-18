from src.apis.ApiManager import ApiManager
from src.constants import AUDIOBOOKSHELF_API_BASE

# TODO: I probably want to use aioaudiobookshelf instead
# https://pypi.org/project/aioaudiobookshelf/

class AudiobookShelfApiManager(ApiManager):
    def __init__(self):
        super().__init__(AUDIOBOOKSHELF_API_BASE)

audiobookshelf_api_manager = AudiobookShelfApiManager()