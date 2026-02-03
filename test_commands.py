"""
Test script to verify correct commands for each instrument
"""
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

print("=" * 60)
print("TESTING CORRECT COMMANDS")
print("=" * 60)

# Test Current Source 6221
print("\n--- TESTING CURRENT SOURCE 6221 ---")
try:
    cs = rm.open_resource("GPIB0::12::INSTR")
    cs.timeout = 5000
    
    print(f"IDN: {cs.query('*IDN?').strip()}")
    
    # Clear errors
    cs.write("*CLS")
    
    # Test current setting (correct command)
    print("\nTesting current commands...")
    cs.write("SOUR:CURR 0.001")
    print("  Set current to 1mA - OK")
    
    # Check for errors
    err = cs.query("SYST:ERR?").strip()
    print(f"  Error check: {err}")
    
    cs.close()
except Exception as e:
    print(f"ERROR: {e}")

# Test Picoammeter 6487
print("\n--- TESTING PICOAMMETER 6487 ---")
try:
    pm = rm.open_resource("GPIB0::22::INSTR")
    pm.timeout = 5000
    
    print(f"IDN: {pm.query('*IDN?').strip()}")
    
    # Clear errors
    pm.write("*CLS")
    
    # The 6487 measures voltage/current, it doesn't source
    print("\nTesting measurement commands...")
    
    # Try to read voltage
    try:
        voltage = pm.query("READ?").strip()
        print(f"  Voltage reading: {voltage}")
    except Exception as e:
        print(f"  READ? failed: {e}")
        
    # Alternative: fetch after initiating
    try:
        pm.write("INIT")
        voltage = pm.query("FETC?").strip()
        print(f"  FETC? reading: {voltage}")
    except Exception as e:
        print(f"  INIT/FETC? failed: {e}")
    
    # Check for errors
    err = pm.query("SYST:ERR?").strip()
    print(f"  Error check: {err}")
    
    pm.close()
except Exception as e:
    print(f"ERROR: {e}")

# Test Switch 3700
print("\n--- TESTING SWITCH 3700 ---")
try:
    sw = rm.open_resource("GPIB0::16::INSTR")
    sw.timeout = 5000
    
    print(f"IDN: {sw.query('*IDN?').strip()}")
    
    # Clear errors
    sw.write("errorqueue.clear()")
    
    print("\nTesting channel commands...")
    
    # Test close channel
    sw.write("channel.close(1002)")
    sw.write("waitcomplete()")
    print("  Closed channel 1002 - OK")
    
    # Check state
    state = sw.query("print(channel.getstate(1002))").strip()
    print(f"  Channel 1002 state: {state} (1=closed, 0=open)")
    
    # Open it again
    sw.write("channel.open(1002)")
    sw.write("waitcomplete()")
    print("  Opened channel 1002 - OK")
    
    # Check for errors
    error = sw.query("print(errorqueue.next())").strip()
    print(f"  Error check: {error}")
    
    sw.close()
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
