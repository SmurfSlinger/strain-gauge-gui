
'''
All instrument classes derive from this base class. It is functionally abstract, meaning it contains certain elements
that the child classes may use, override (change the functionality), or ignore entirely.
This class will not and should be not used directly. Only instantiate subclasses of this class.
'''

import pyvisa


class BaseInstrument:
    def __init__(self, resource_name: str, name: str = "None"):
        self.resource_name = resource_name
        self.name = name
        self.rm = None
        self.inst = None
        self.connected = False
        self.idn = None

    def connect(self) -> str:
        """
        Open VISA connection and verify instrument identity.
        Returns *IDN? string on success.
        Raises Exception on failure.
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(self.resource_name)
        self.inst.timeout = 5000

        self.idn = self.inst.query("*IDN?").strip()
        self.connected = True
        return self.idn

    def disconnect(self):
        if self.inst:
            try:
                self.inst.close()
            except Exception:
                pass
        self.inst = None
        self.connected = False
