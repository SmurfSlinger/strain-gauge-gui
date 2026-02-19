import os
import pyvisa

# If needed (you already used this before)
os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

RESOURCE = "GPIB0::26::INSTR"  # <-- CHANGE if needed

rm = pyvisa.ResourceManager()
inst = rm.open_resource(RESOURCE)

inst.timeout = 5000  # 5 seconds

print("Connected to:", inst.query("*IDN?").strip())

# --- Put DMM into resistance mode ---
inst.write("dmm.func = dmm.FUNC_RES")
inst.write("dmm.range = dmm.RANGE_AUTO")

# --- Open all channels first ---
inst.write('channel.open("all")')

# --- Close one channel (change number if needed) ---
CHANNEL = 1002
inst.write(f"channel.close({CHANNEL})")
inst.write("waitcomplete()")

# --- Measure resistance ---
response = inst.query("print(dmm.measure())").strip()

print("Measured resistance:", response)

# Cleanup (optional)
inst.write(f"channel.open({CHANNEL})")

inst.close()
rm.close()













