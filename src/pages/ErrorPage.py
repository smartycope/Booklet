from src.pages.StaticTextPage import StaticTextPage

class ErrorPage(StaticTextPage):
    def __init__(self, error: Exception):
        super().__init__(
            str(error)
        )

    async def center_pressed(self):
        return 'Landing'
