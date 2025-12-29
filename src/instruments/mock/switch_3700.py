from src.instruments.abstract.switch_matrix import SwitchMatrix

class MockSwitch3700(SwitchMatrix):
    def __init__(self):
        super().__init__("Mock3700")
        self.closed_channels = set()
        self.connected = False

    def connect(self):
        self.connected = True

    def write(self, command: str):
        if "CLOSe" in command:
            ch = int(command.split("@")[1].strip(")"))
            self.closed_channels.add(ch)
        elif "OPEN" in command:
            if "@(" in command:
                ch = int(command.split("@")[1].strip(")"))
                self.closed_channels.discard(ch)
            else:
                self.closed_channels.clear()

    def query(self, command: str) -> str:
        return "0"

    def close_channel(self, channel: int):
        self.closed_channels.add(channel)

    def open_channel(self, channel: int):
        self.closed_channels.discard(channel)

    def open_all(self):
        self.closed_channels.clear()