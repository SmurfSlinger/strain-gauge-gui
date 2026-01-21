from abc import ABC

from src.instruments.abstract.switch_matrix import SwitchMatrix

class Switch3700(SwitchMatrix, ABC):
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

    def open_all(self):
        """
        Open all channels on the switch matrix.
        """
        if not self.connected:
            return

        # Keithley SCPI: open all channels
        self.inst.write("ROUTe:OPEN:ALL")
        self.closed_channels.clear()

    def close_channel(self, channel: int):
        """
        Close a single channel.
        """
        if not self.connected:
            return

        # Keithley SCPI: close specific channel
        self.inst.write(f"ROUTe:CLOSe (@{channel})")
        self.closed_channels.add(channel)

    def open_channel(self, channel: int):
        """
        Open a single channel.
        """
        if not self.connected:
            return

        self.inst.write(f"ROUTe:OPEN (@{channel})")
        self.closed_channels.discard(channel)

        # -------------------------
        # Optional helpers (safe)
        # -------------------------

    def reset(self):
        """
        Reset the switch to power-on defaults.
        """
        if not self.connected:
            return

        self.inst.write("*RST")
        self.closed_channels.clear()