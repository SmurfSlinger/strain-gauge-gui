import os
import pyvisa

os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

RESOURCE = "GPIB0::16::INSTR"

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

# FIX: Use write() then read() instead of query()
inst.write("print(dmm.measure())")
resistance = inst.read().strip()
print(f"Resistance: {resistance} Ohms")

inst.close()
rm.close()
