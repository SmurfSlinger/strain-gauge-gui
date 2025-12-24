from src.instruments.switch_multimeter import Switch3700

class MockSwitch3700(Switch3700):
    def __init__(self):
        super().__init__("Mock3700")
        self.closed_channels = set()

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