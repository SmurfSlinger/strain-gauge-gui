"""
Thoroughly clear and verify all instruments are error-free
"""
import pyvisa
import time

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

print("=" * 60)
print("THOROUGH ERROR CLEARING")
print("=" * 60)

# Switch 3700
print("\n--- Switch 3700 ---")
try:
    sw = rm.open_resource("GPIB0::16::INSTR")
    sw.timeout = 5000
    
    # Clear multiple times to flush queue
    for i in range(3):
        sw.write("errorqueue.clear()")
        time.sleep(0.1)
    
    # Verify empty
    error = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in error or error.startswith("0"):
        print("  [OK] Error queue cleared")
    else:
        print(f"  [WARNING] Still has error: {error}")
    
    sw.close()
except Exception as e:
    print(f"  [FAIL] {e}")

# Current Source 6221
print("\n--- Current Source 6221 ---")
try:
    cs = rm.open_resource("GPIB0::12::INSTR")
    cs.timeout = 5000
    
    # Clear multiple times
    for i in range(3):
        cs.write("*CLS")
        time.sleep(0.1)
    
    # Verify empty
    error = cs.query("SYST:ERR?").strip()
    if error.startswith("+0,") or error.startswith("0,"):
        print("  [OK] Error queue cleared")
    else:
        print(f"  [WARNING] Still has error: {error}")
    
    cs.close()
except Exception as e:
    print(f"  [FAIL] {e}")

# Picoammeter 6487
print("\n--- Picoammeter 6487 ---")
try:
    pm = rm.open_resource("GPIB0::22::INSTR")
    pm.timeout = 5000
    
    # Clear multiple times
    for i in range(3):
        pm.write("*CLS")
        time.sleep(0.1)
    
    # Verify empty
    error = pm.query("SYST:ERR?").strip()
    if error.startswith("+0,") or error.startswith("0,"):
        print("  [OK] Error queue cleared")
    else:
        print(f"  [WARNING] Still has error: {error}")
    
    pm.close()
except Exception as e:
    print(f"  [FAIL] {e}")

print("\n" + "=" * 60)
print("Done! All instruments should be error-free now.")
print("=" * 60)
