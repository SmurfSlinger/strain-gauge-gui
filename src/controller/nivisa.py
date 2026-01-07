import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource("ASRL3::INSTR")

