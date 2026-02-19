import os
import pyvisa

import os

os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

rm = pyvisa.ResourceManager()
print("Available resources:")
print(rm.list_resources())



# If needed (you already used this before)
os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

RESOURCE = "GPIB0::16::INSTR"  # <-- CHANGE if needed

rm = pyvisa.ResourceManager()
inst = rm.open_resource(RESOURCE)

inst.timeout = 5000  # 5 seconds

print("Connected to:", inst.query("*IDN?").strip())

inst.write("reset()")

inst.write("dmm.func = dmm.FUNC_RES")

inst.write('channel.open("all")')
inst.write("waitcomplete()")

inst.write("channel.close(1001)")
inst.write("waitcomplete()")

print(inst.query("print(dmm.measure())"))

inst.close()
rm.close()











