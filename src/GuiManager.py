from functools import partial
from src.pages.Page import Page

class GuiManager:
    """ Manage the connection between the screen and the pages. Handles events, and switches between pages. """
    def __init__(self, screen, pages:dict[str, Page], start_page: str):
        self.screen = screen
        self.pages = pages
        self.goto_page(start_page)

        # Connect all the events
        self.screen.gpio_key_up_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key_down_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key_left_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key_right_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key_center_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key1_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key2_pin.when_pressed = partial(self.handle_event, event='pressed')
        self.screen.gpio_key3_pin.when_pressed = partial(self.handle_event, event='pressed')

        self.screen.gpio_key_up_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key_down_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key_left_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key_right_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key_center_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key1_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key2_pin.when_released = partial(self.handle_event, event='released')
        self.screen.gpio_key3_pin.when_released = partial(self.handle_event, event='released')

        self.screen.gpio_key_up_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key_down_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key_left_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key_right_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key_center_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key1_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key2_pin.when_held = partial(self.handle_event, event='held')
        self.screen.gpio_key3_pin.when_held = partial(self.handle_event, event='held')

    def handle_event(self, device, event=None):
        match event:
            case 'pressed':
                match device:
                    case self.screen.gpio_key_up_pin:
                        rtn = self.current_page.up_pressed()
                    case self.screen.gpio_key_down_pin:
                        rtn = self.current_page.down_pressed()
                    case self.screen.gpio_key_left_pin:
                        rtn = self.current_page.left_pressed()
                    case self.screen.gpio_key_right_pin:
                        rtn = self.current_page.right_pressed()
                    case self.screen.gpio_key_center_pin:
                        rtn = self.current_page.center_pressed()
                    case self.screen.gpio_key1_pin:
                        rtn = self.current_page.key1_pressed()
                    case self.screen.gpio_key2_pin:
                        rtn = self.current_page.key2_pressed()
                    case self.screen.gpio_key3_pin:
                        rtn = self.current_page.key3_pressed()
                    case _:
                        raise ValueError(f"Unknown device: {device}")
            case 'released':
                match device:
                    case self.screen.gpio_key_up_pin:
                        rtn = self.current_page.up_released()
                    case self.screen.gpio_key_down_pin:
                        rtn = self.current_page.down_released()
                    case self.screen.gpio_key_left_pin:
                        rtn = self.current_page.left_released()
                    case self.screen.gpio_key_right_pin:
                        rtn = self.current_page.right_released()
                    case self.screen.gpio_key_center_pin:
                        rtn = self.current_page.center_released()
                    case self.screen.gpio_key1_pin:
                        rtn = self.current_page.key1_released()
                    case self.screen.gpio_key2_pin:
                        rtn = self.current_page.key2_released()
                    case self.screen.gpio_key3_pin:
                        rtn = self.current_page.key3_released()
                    case _:
                        raise ValueError(f"Unknown device: {device}")
            case 'held':
                match device:
                    case self.screen.gpio_key_up_pin:
                        rtn = self.current_page.up_held()
                    case self.screen.gpio_key_down_pin:
                        rtn = self.current_page.down_held()
                    case self.screen.gpio_key_left_pin:
                        rtn = self.current_page.left_held()
                    case self.screen.gpio_key_right_pin:
                        rtn = self.current_page.right_held()
                    case self.screen.gpio_key_center_pin:
                        rtn = self.current_page.center_held()
                    case self.screen.gpio_key1_pin:
                        rtn = self.current_page.key1_held()
                    case self.screen.gpio_key2_pin:
                        rtn = self.current_page.key2_held()
                    case self.screen.gpio_key3_pin:
                        rtn = self.current_page.key3_held()
                    case _:
                        raise ValueError(f"Unknown device: {device}")

        # If the handler returns a string, goto that page
        # using type is intentional here: returns are almost always going to be literal
        if type(rtn) is str:
            self.goto_page(rtn)
        if isinstance(rtn, tuple):
            # If the handler returns a tuple of a string and a dictionary, goto that page, and set those
            # attributes on the page class
            if type(rtn[0]) is str and type(rtn[1]) is dict:
                self.goto_page(rtn[0], rtn[1])
            # If the handler returns a tuple of 4 integers, partial update (should be a tuple of 4 integers)
            # x1, x2, y1, y2
            elif len(rtn) == 4:
                self.render(rtn)
            else:
                raise ValueError(f"Invalid tuple: {rtn}")
        # If the handler returns True, render the current page
        elif rtn:
            self.render()
        # If the handler returns None, no modifications to self.current_page.img were made

    def render(self, window=()):
        self.screen.show_image(self.current_page.img, *window)

    @property
    def current_page(self):
        return self.pages[self.current_page_name]

    def goto_page(self, name:str, data:dict={}):
        if isinstance(name, str):
            if name in self.pages:
                self.current_page_name = name
                for k, v in data.items():
                    setattr(self.current_page.__class__, k, v)
                self.render()
            else:
                raise ValueError(f"Page with name {name} does not exist")
        else:
            raise ValueError(f"Page name must be a string, not {type(name)}")

    def run(self):
        self.screen.listen()