from src import THEME
from src.pages.Page import Page


class LoadingPage(Page):
    """Non-interactive page shown while an async route is being constructed."""

    def __init__(self, message="Loading…"):
        super().__init__()
        width = self.draw.textlength(message, font=THEME["font"])
        bbox = self.draw.textbbox((0, 0), message, font=THEME["font"])
        height = bbox[3] - bbox[1]
        self.text(message, (self.width - width) / 2, (self.height - height) / 2)
