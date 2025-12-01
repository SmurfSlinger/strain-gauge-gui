import pyvisa
from pyvisa.constants import StopBits, Parity

# Test connected instrument
rm = pyvisa.ResourceManager()
print(rm.list_resources())


instr = rm.open_resource("ASRL3::INSTR")

instr.baud_rate = 9600
instr.data_bits = 8
instr.parity = Parity.none
instr.stop_bits = StopBits.one
instr.write_termination = '\r\n'
instr.read_termination = '\r\n'
instr.timeout = 5000

# Ask what instrument it is

try:
    print("ID:", instr.query("*IDN?"))
except Exception as e:
    print("Error:", e)