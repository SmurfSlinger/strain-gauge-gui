import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
inst = rm.open_resource("GPIB0::16::INSTR")
inst.timeout = 5000

print(inst.query("print(slot[2].installed)"))
print(inst.query("print(slot[3].installed)"))
















