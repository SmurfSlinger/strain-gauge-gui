from src.instruments.base_instrument import BaseInstrument

class Switch3700(BaseInstrument):
    def close_channel(self, channel: int):
        self.write(f"ROUTe:Close (@{channel})")     # write() is what sends commands to the machine

    def open_channel(self, channel: int):
        self.write(f"ROUTe:OPEN (@{channel})")

    def open_all(self):
        self.write(f"ROUTe:OPEN:ALL")