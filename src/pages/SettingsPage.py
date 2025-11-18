from src.pages.ListPage import ListPage


class SettingsPage(ListPage):
    def __init__(self):
        super().__init__(
            items=['Brightness', 'Volume'],
            scrollable=False,
            title="Settings",
            right_pressed='landing'
        )

    def up_pressed(self):
        if self.selected_index == 0:
            return 'landing'
        return super().up_pressed()
