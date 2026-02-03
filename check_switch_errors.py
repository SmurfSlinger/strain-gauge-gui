"""
Check only the switch error queue
"""
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

print("Checking Switch 3700 error queue...")
sw = rm.open_resource("GPIB0::16::INSTR")
sw.timeout = 5000

print(f"IDN: {sw.query('*IDN?').strip()}")

print("\nError Queue:")
for i in range(10):
    error = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in error or error == "0" or error.startswith("0"):
        print("  (empty)")
        break
    print(f"  {error}")

sw.close()
