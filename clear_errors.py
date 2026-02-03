"""
Clear all error queues on all instruments
"""
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

print("Clearing all instrument error queues...")

# Clear Switch 3700
try:
    sw = rm.open_resource("GPIB0::16::INSTR")
    sw.timeout = 5000
    sw.write("errorqueue.clear()")
    print("✓ Switch 3700 errors cleared")
    sw.close()
except Exception as e:
    print(f"✗ Switch 3700: {e}")

# Clear Current Source 6221
try:
    cs = rm.open_resource("GPIB0::12::INSTR")
    cs.timeout = 5000
    cs.write("*CLS")
    print("✓ Current Source 6221 errors cleared")
    cs.close()
except Exception as e:
    print(f"✗ Current Source 6221: {e}")

# Clear Picoammeter 6487
try:
    pm = rm.open_resource("GPIB0::22::INSTR")
    pm.timeout = 5000
    pm.write("*CLS")
    print("✓ Picoammeter 6487 errors cleared")
    pm.close()
except Exception as e:
    print(f"✗ Picoammeter 6487: {e}")

print("\nDone! All error queues cleared.")
