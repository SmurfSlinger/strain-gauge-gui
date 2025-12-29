from abc import abstractmethod, ABC


class SwitchMatrix(ABC):
    def __init__(self, controller):
        self.controller = controller

    @abstractmethod             # This must be defined in child classes
    def close_channel(self, channel: int):
        pass

    @abstractmethod             # This must be defined in child classes
    def open_channel(self, channel: int):
        pass

    @abstractmethod             # This must be defined in child classes
    def open_all(self):
        pass

    @abstractmethod
    def query(self, command: str):
        pass
