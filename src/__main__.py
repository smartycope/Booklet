import asyncio
import aiohttp
from src.GuiManager import GuiManager
from src.AudiobookshelfApiManager import AudiobookshelfApiManager
from src.AudioPlayer import AudioPlayer
from src.pages.ErrorPage import ErrorPage
from src.screens.SimulatedScreen import SimulatedScreen
from src.screens.Screen import Screen
from src import DEBUG

from src.pages.LandingPage import LandingPage



# async def main():
#     async with aiohttp.ClientSession() as session:
#         api = AudiobookshelfApiManager(session)

#     manager.goto_page("landing")
#     manager.run()


# if __name__ == "__main__":
#     asyncio.run(main())

# PAGES = {
#     "landing": LandingPage(),

#     "audiobookshelf landing": AudiobookshelfLandingPage(),
#     "audiobookshelf local": LocalBooksPage(),
#     "audiobookshelf download": SelectBookPage(),

#     "settings": SettingsPage(),
#     "brightness": BrightnessPage(),
#     "volume": VolumePage(),
#     "bluetooth": BluetoothPage(),
# }


async def main():
    # This number was chosen by trial and error. For a different monitor,
    # you may need to adjust this number.
    # rescale = (83, 83)
    rescale = False
    screen = SimulatedScreen(rescale) if DEBUG else Screen()
    player = AudioPlayer()

    connector = aiohttp.TCPConnector(limit=4)
    async with aiohttp.ClientSession(connector=connector) as session:
        api = await AudiobookshelfApiManager.create(session)

        manager = GuiManager(player, api, screen, await LandingPage())
        # manager.goto_page("landing")

        # gui.run() blocks, so don't run it directly on the asyncio thread.
        # await asyncio.to_thread(manager.run)
        try:
            await manager.run()
        except Exception as err:
            manager.current_page = ErrorPage(err)


if __name__ == "__main__":
    asyncio.run(main())
