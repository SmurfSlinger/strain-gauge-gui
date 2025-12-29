from operator import truediv

'''
All instrument classes derive from this base class. It is functionally abstract, meaning it contains certain elements
that the child classes may use, override (change the functionality), or ignore entirely.
This class will not and should be not used directly. Only instantiate subclasses of this class.
'''

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

    def reset(self):
        raise NotImplementedError