import os
import pyvisa

os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

RESOURCE = "GPIB0::16::INSTR"

rm = pyvisa.ResourceManager()
inst = rm.open_resource(RESOURCE)

inst.timeout = 5000  # 5 seconds

print("Connected to:", inst.query("*IDN?").strip())

inst.write("reset()")
inst.write("errorqueue.clear()")
inst.write('channel.open("allslots")')
inst.write('dmm.setconfig("slot1","fourwireohms")')
inst.write('scan.create("1001")')

inst.write("mybuf = dmm.makebuffer(10)")
inst.write('scan.scancount = 1')
inst.write('scan.execute(mybuf)')

print(inst.query("print(mybuf.readings[1])"))

inst.close()
rm.close()
