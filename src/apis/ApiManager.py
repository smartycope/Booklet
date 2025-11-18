from abc import ABC

class ApiManager(ABC):
    def __init__(self, base):
        self.base = base
        self.timeout = 10
