from src import CONFIG, DEBUG, KEYS, AUDIOBOOKSHELF_API_BASE as HOST
import aioaudiobookshelf as abs
# import asyncio
import aiohttp
from aioaudiobookshelf import SessionConfiguration, UserClient
from aioaudiobookshelf.schema.library import LibraryItemMinifiedBook
# from pathlib import Path
# import json

# https://pypi.org/project/aioaudiobookshelf/

class AudiobookshelfApiManager:
    pagination_items_per_page = 5
    in_progress_filter = 'progress.aW4tcHJvZ3Jlc3M%3D'

    # async def __init__(self, session: aiohttp.ClientSession):
    #     self.client = await abs.get_user_client_by_token(
    #         session_config=SessionConfiguration(
    #             session=session, url=HOST, pagination_items_per_page=5, token=KEYS['audiobookshelf_api_key']
    #         )
    #     )

    #     self.library_id = CONFIG.get('library_id', await self.get_library_id(self.client))


    def __init__(self, client, library_id):
        self.client = client
        self.library_id = library_id

    @classmethod
    async def create(cls, session: aiohttp.ClientSession):
        client = await abs.get_user_client_by_token(
            session_config=SessionConfiguration(
                session=session,
                url=HOST,
                pagination_items_per_page=5,
                token=KEYS["audiobookshelf_api_key"],
            )
        )

        library_id = CONFIG.get("library_id")
        if library_id is None:
            library_id = await cls._find_library_id(client)

        return cls(client, library_id)


    @staticmethod
    async def _find_library_id(client: UserClient):
        for library in await client.get_all_libraries():
            if library.name == KEYS["audiobookshelf_library_name"]:
                CONFIG["library_id"] = library.id_
                CONFIG.sync()
                return library.id_

        raise RuntimeError("Configured Audiobookshelf library was not found")


    # async def get_library_id(self, client: UserClient):
    #     for lib in await client.get_all_libraries():
    #         if lib.name == KEYS['audiobookshelf_library_name']:
    #             CONFIG['library_id'] = lib.id_
    #             CONFIG.sync()
    #             return lib.id_

    async def get_titles_from_ids(self, item_ids):
        books = await self.client.get_library_item_batch_book(item_ids=item_ids)
        return [book.media.metadata.title for book in books]

    async def expand_books(self, books):
        return await self.client.get_library_item_batch_book(item_ids=[b.id_ for b in books])

    async def _get_books(self, library_id, filter_id=None):
        books = []
        async for response in self.client.get_library_items(library_id=library_id, filter_str=filter_id):
            print(f"Fetched {len(response.results)} items from library {library_id}")
            if not response.results:
                break
            books.extend([b for b in response.results if isinstance(b, LibraryItemMinifiedBook)])
        return books

    async def get_books(self, library_id, in_progress=False, expanded=False):
        if in_progress:
            filter_str = self.in_progress_filter
        else:
            filter_str = None

        books = await self._get_books(library_id, filter_id=filter_str)
        if expanded:
            return await self.expand_books(books)
        return books

        # books = await get_books(client, library_id, in_progress=True, expanded=True)
        # # display(await get_titles_from_ids(client, [b.id_ for b in books]))
        # display([b.media.metadata.title for b in books])
        # book = (await client.get_library_item_batch_book(item_ids=[b.id_ for b in books]))[0]


    # asyncio.run(abs_basics())
