import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
sw = rm.open_resource("GPIB0::16::INSTR")

sw.write('channel.close("1002")')
sw.write("waitcomplete()")

state = sw.query("print(channel.getstate('1002'))")
print("Channel 1002 State:", state)

for i in range(1,7):
    print(f"Slot {i}:",
          sw.query(f"print(slot[{i}].model)"),
          sw.query(f"print(slot[{i}].description)"))

sw.write("print(errorqueue.next())")