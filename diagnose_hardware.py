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
    voltmeter.timeout = 10000  # Longer timeout for slow instrument
    
    # Clear buffer first
    voltmeter.write("*CLS")
    time.sleep(0.2)
    
    idn = voltmeter.query("*IDN?").strip()
    print(f"   [OK] Connected: {idn}")
    
    # Test voltage measurement - configure properly
    print("   Configuring for voltage measurements...")
    voltmeter.write("*RST")  # Reset to known state
    time.sleep(0.5)
    
    voltmeter.write("SOUR:VOLT:STAT OFF")  # Turn OFF voltage source
    voltmeter.write("SOUR:VOLT:RANG 50")  # Set voltage source range
    voltmeter.write("SENS:FUNC 'VOLT'")  # Set to voltage measurement mode
    voltmeter.write("SENS:VOLT:RANG:AUTO ON")  # Auto-range
    voltmeter.write("FORM:ELEM READ")  # Format: reading only
    voltmeter.write("SYST:ZCH OFF")  # Disable zero check
    voltmeter.write("ARM:SOUR IMM")  # Immediate arming
    voltmeter.write("ARM:COUN 1")  # Single reading
    voltmeter.write("*CLS")  # Clear errors
    time.sleep(0.3)
    
    print("   Taking a test voltage reading...")
    try:
        # Initiate reading
        voltmeter.write("INIT")
        time.sleep(0.2)
        # Fetch the reading
        v = voltmeter.query("FETC?")
        print(f"   [OK] Voltage reading: {v.strip()} V")
    except Exception as e:
        print(f"   [FAIL] Read failed: {e}")
        print(f"   Trying alternate method...")
        try:
            # Try READ? which initiates and fetches
            v = voltmeter.query("READ?")
            print(f"   [OK] Voltage reading (alternate): {v.strip()} V")
        except Exception as e2:
            print(f"   [FAIL] Alternate method also failed: {e2}")
    
    voltmeter.close()
except Exception as e:
    print(f"   [FAIL] ERROR: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
print("\nIf all tests passed, the hardware is working correctly.")
print("If the GUI still doesn't work, the issue is in the software.")

input("\nPress Enter to exit...")
