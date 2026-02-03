"""
Diagnostic script to test instrument communication
Run this to verify hardware is responding before using the GUI
"""
import pyvisa
import time

print("=" * 60)
print("INSTRUMENT DIAGNOSTIC TEST")
print("=" * 60)

# Initialize VISA
rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

# Test 1: List all instruments
print("\n1. Scanning for GPIB instruments...")
try:
    resources = rm.list_resources()
    print(f"   Found {len(resources)} instruments:")
    for r in resources:
        print(f"   - {r}")
except Exception as e:
    print(f"   ERROR: {e}")
    input("\nPress Enter to exit...")
    exit(1)

# Test 2: Connect to switch (3706A)
print("\n2. Testing Switch (GPIB0::16::INSTR)...")
try:
    switch = rm.open_resource("GPIB0::16::INSTR")
    switch.timeout = 5000
    idn = switch.query("*IDN?").strip()
    print(f"   [OK] Connected: {idn}")
    
    # Test open/close channel
    print("   Testing channel control...")
    switch.write("channel.open('allslots')")
    switch.write("waitcomplete()")
    time.sleep(0.2)
    
    switch.write("channel.close(1001)")
    switch.write("waitcomplete()")
    print("   [OK] Channel 1001 closed (you should hear 1 click)")
    time.sleep(1)
    
    switch.write("channel.open(1001)")
    switch.write("waitcomplete()")
    print("   [OK] Channel 1001 opened (you should hear 1 click)")
    
    switch.close()
except Exception as e:
    print(f"   [FAIL] ERROR: {e}")

# Test 3: Connect to current source (6221)
print("\n3. Testing Current Source (GPIB0::12::INSTR)...")
try:
    current = rm.open_resource("GPIB0::12::INSTR")
    current.timeout = 5000
    idn = current.query("*IDN?").strip()
    print(f"   [OK] Connected: {idn}")
    
    # Don't actually turn on output for safety
    print("   [OK] Communication OK (not enabling output for safety)")
    
    current.close()
except Exception as e:
    print(f"   [FAIL] ERROR: {e}")

# Test 4: Connect to picoammeter/voltage source (6487)
print("\n4. Testing Picoammeter/Voltage Source (GPIB0::22::INSTR)...")
try:
    voltmeter = rm.open_resource("GPIB0::22::INSTR")
    voltmeter.timeout = 5000
    
    # Clear buffer first
    voltmeter.write("*CLS")
    time.sleep(0.2)
    
    idn = voltmeter.query("*IDN?").strip()
    print(f"   [OK] Connected: {idn}")
    
    # Test voltage measurement
    voltmeter.write("FORM:ELEM READ")
    voltmeter.write("NPLC 0.01")
    voltmeter.write("SYST:ZCH OFF")
    voltmeter.write("SOUR:VOLT:STAT OFF")  # Turn OFF voltage source
    voltmeter.write("*CLS")
    time.sleep(0.2)
    
    print("   Taking a test voltage reading...")
    try:
        v = voltmeter.query("READ?")
        print(f"   [OK] Voltage reading: {v.strip()} V")
    except Exception as e:
        print(f"   [FAIL] Read failed: {e}")
    
    voltmeter.close()
except Exception as e:
    print(f"   [FAIL] ERROR: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
print("\nIf all tests passed, the hardware is working correctly.")
print("If the GUI still doesn't work, the issue is in the software.")

input("\nPress Enter to exit...")
