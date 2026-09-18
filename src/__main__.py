import asyncio
import aiohttp
import logging
from src.GuiManager import GuiManager
from src.AudiobookshelfApiManager import AudiobookshelfApiManager
from src.AudioPlayer import AudioPlayer
from src.pages.ErrorPage import ErrorPage
from src.screens.SimulatedScreen import SimulatedScreen
from src.screens.Screen import Screen
from src import DEBUG

from src.pages.LandingPage import LandingPage


AUDIOBOOKSHELF_CONNECTION_ERROR = None


async def connect_audiobookshelf(session):
    global AUDIOBOOKSHELF_CONNECTION_ERROR
    AUDIOBOOKSHELF_CONNECTION_ERROR = None
    try:
        return await AudiobookshelfApiManager.create(session)
    except Exception as error:
        AUDIOBOOKSHELF_CONNECTION_ERROR = error
        logging.exception(
            "Could not connect to Audiobookshelf; continuing in offline mode"
        )
        return None


async def main():
    # This number was chosen by trial and error. For a different monitor,
    # you may need to adjust this number.
    # rescale = (83, 83)
    rescale = False
    screen = SimulatedScreen(rescale) if DEBUG else Screen()
    player = AudioPlayer()

    connector = aiohttp.TCPConnector(limit=4)
    async with aiohttp.ClientSession(connector=connector) as session:
        api = await connect_audiobookshelf(session)

        manager = GuiManager(
            player,
            api,
            screen,
            await LandingPage(),
            api_error=AUDIOBOOKSHELF_CONNECTION_ERROR,
        )

        try:
            await manager.run()
        except Exception as err:
            logging.exception("Booklet stopped because of an unhandled error")
            manager.current_page = ErrorPage(err)
        finally:
            await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
