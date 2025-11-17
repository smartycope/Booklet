from .Page import Page
from .StaticPage import StaticPage
# from .ListPage import ListPage
# from .PlayerPage import PlayerPage

from .LandingPage import LandingPage
from .TestPage import TestPage

pages = {
    "landing": LandingPage(),
    "test": TestPage(),
}

