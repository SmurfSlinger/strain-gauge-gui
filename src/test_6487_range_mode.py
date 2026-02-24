"""
Query the 6487 to find out what commands it actually supports.
"""
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
inst = rm.open_resource("GPIB0::22::INSTR")
inst.timeout = 5000

print("6487 Command Discovery")
print("=" * 70)

# Test 1: Can we query current settings?
print("\nTest 1: Query current configuration")
test_queries = [
    "FUNC?",
    "SENS:FUNC?", 
    "CONF?",
    "SYST:FUNC?",
    "VOLT:RANG?",
    "CURR:RANG?",
]

for query in test_queries:
    try:
        inst.write("*CLS")
        result = inst.query(query).strip()
        print(f"  {query} -> {result}")
    except Exception as e:
        print(f"  {query} -> ERROR: {e}")

# Test 2: Try range-based approach (maybe it auto-detects mode from range?)
print("\n\nTest 2: Setting voltage vs current range")
print("Trying to set VOLTAGE range (should switch to voltage mode)...")

try:
    inst.write("*CLS")
    inst.write("VOLT:RANG 2")  # Set 2V range
    error = inst.query("SYST:ERR?").strip()
    print(f"  VOLT:RANG 2 -> {error}")
    
    # Take a reading
    reading = inst.query("READ?").strip()
    print(f"  Reading after VOLT:RANG: {reading}")
    
except Exception as e:
    print(f"  ERROR: {e}")

print("\n\nTest 3: What does the manual say?")
print("Check if 6487 has a 'ZERO CHECK' that must be disabled...")

try:
    inst.write("*CLS")
    # Turn off zero check
    inst.write("SYST:ZCH OFF")
    
    # Set to voltage range
    inst.write("VOLT:RANG:AUTO ON")
    
    error = inst.query("SYST:ERR?").strip()
    print(f"  After SYST:ZCH OFF and VOLT:RANG:AUTO ON -> {error}")
    
    # Try reading
    reading = inst.query("READ?").strip()
    print(f"  Reading: {reading}")
    
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 70)
print("Check 6487 front panel - what units does it show NOW?")
print("If it shows V or mV, the VOLT:RANG command worked!")
print("=" * 70)

inst.close()
rm.close()
