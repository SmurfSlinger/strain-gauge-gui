from operator import truediv


class BaseInstrument:
    def __init__(self, name):
        self.name = name
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def write(self, command: str):
        raise NotImplementedError()

    def query(self, command: str) -> str:
        raise NotImplementedError()