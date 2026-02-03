"""
Diagnostic script to check errors on all three instruments
"""
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

print("=" * 60)
print("CHECKING INSTRUMENT ERRORS")
print("=" * 60)

# Check Switch 3700 (GPIB address 16)
print("\n--- SWITCH 3700 (GPIB0::16::INSTR) ---")
try:
    switch = rm.open_resource("GPIB0::16::INSTR")
    switch.timeout = 5000
    
    print(f"IDN: {switch.query('*IDN?').strip()}")
    
    # Read all errors from queue
    print("\nError Queue:")
    for i in range(10):  # Read up to 10 errors
        error = switch.query("print(errorqueue.next())").strip()
        if "Queue Is Empty" in error or error == "0":
            print("  (empty)")
            break
        print(f"  {error}")
    
    switch.close()
except Exception as e:
    print(f"ERROR: {e}")

# Check Current Source 6221 (GPIB address 12)
print("\n--- CURRENT SOURCE 6221 (GPIB0::12::INSTR) ---")
try:
    current_source = rm.open_resource("GPIB0::12::INSTR")
    current_source.timeout = 5000
    
    print(f"IDN: {current_source.query('*IDN?').strip()}")
    
    # Read error queue (SCPI standard)
    print("\nError Queue:")
    for i in range(10):
        error = current_source.query("SYST:ERR?").strip()
        if error.startswith("+0,") or error.startswith("0,"):
            print("  (empty)")
            break
        print(f"  {error}")
    
    current_source.close()
except Exception as e:
    print(f"ERROR: {e}")

# Check Picoammeter 6487 (GPIB address 22)
print("\n--- PICOAMMETER 6487 (GPIB0::22::INSTR) ---")
try:
    picoammeter = rm.open_resource("GPIB0::22::INSTR")
    picoammeter.timeout = 5000
    
    print(f"IDN: {picoammeter.query('*IDN?').strip()}")
    
    # Read error queue (SCPI standard)
    print("\nError Queue:")
    for i in range(10):
        error = picoammeter.query("SYST:ERR?").strip()
        if error.startswith("+0,") or error.startswith("0,"):
            print("  (empty)")
            break
        print(f"  {error}")
    
    # Check current status
    print("\nCurrent status:")
    print(f"  Output enabled: {picoammeter.query('OUTP?').strip()}")
    
    picoammeter.close()
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
