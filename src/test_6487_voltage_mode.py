"""
Test all possible SCPI command variations to switch 6487 to VOLTAGE mode.
Run this to find which syntax works without error -150.
"""
import pyvisa
import time

# Connect to 6487
rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
inst = rm.open_resource("GPIB0::22::INSTR")
inst.timeout = 5000

print("=" * 70)
print("6487 VOLTAGE MODE SYNTAX TEST")
print("=" * 70)
print()

# List of different syntax variations to try
test_commands = [
    # Format 1: SENS:FUNC with different quote styles
    ("SENS:FUNC 'VOLT'", "Single quotes with SENS prefix"),
    ('SENS:FUNC "VOLT"', "Double quotes with SENS prefix"),
    ("SENS:FUNC VOLT", "No quotes with SENS prefix"),
    
    # Format 2: FUNC without SENS prefix
    ("FUNC 'VOLT'", "Single quotes without SENS"),
    ('FUNC "VOLT"', "Double quotes without SENS"),
    ("FUNC VOLT", "No quotes without SENS"),
    
    # Format 3: Alternative spellings
    ("SENS:FUNC 'VOLTAGE'", "Full word VOLTAGE with single quotes"),
    ('SENS:FUNC "VOLTAGE"', "Full word VOLTAGE with double quotes"),
    ("FUNC:VOLT", "Short form FUNC:VOLT"),
    
    # Format 4: Using configure command
    ("CONF:VOLT", "CONF:VOLT"),
    ("CONF:VOLT:DC", "CONF:VOLT:DC"),
]

working_commands = []

for i, (cmd, description) in enumerate(test_commands, 1):
    print(f"Test {i}/{len(test_commands)}: {description}")
    print(f"  Command: {cmd}")
    
    try:
        # Clear errors first
        inst.write("*CLS")
        time.sleep(0.1)
        
        # Try the command
        inst.write(cmd)
        time.sleep(0.2)
        
        # Check for errors
        error = inst.query("SYST:ERR?").strip()
        
        if error.startswith("0,") or "No error" in error:
            print(f"  Result: SUCCESS - No errors!")
            
            # Verify what mode we're actually in
            try:
                # Try to query the function
                current_func = inst.query("FUNC?").strip()
                print(f"  Current mode: {current_func}")
            except:
                print(f"  Current mode: (could not query)")
            
            working_commands.append((cmd, description))
            print()
        else:
            print(f"  Result: FAILED - {error}")
            print()
    
    except Exception as e:
        print(f"  Result: EXCEPTION - {e}")
        print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)

if working_commands:
    print(f"\nFOUND {len(working_commands)} WORKING COMMAND(S):\n")
    for cmd, desc in working_commands:
        print(f"  {cmd}")
        print(f"    ({desc})")
        print()
    
    print("=" * 70)
    print("RECOMMENDED COMMAND TO USE:")
    print("=" * 70)
    print(f"\n  {working_commands[0][0]}\n")
else:
    print("\nNO WORKING COMMANDS FOUND!")
    print("The 6487 may require a different approach.")
    print()

# Final test: Try to take a reading and see what we get
print("=" * 70)
print("FINAL TEST: Taking a reading")
print("=" * 70)

try:
    inst.write("*CLS")
    reading = inst.query("READ?").strip()
    print(f"Reading: {reading}")
    
    # Check what the reading looks like
    value = float(reading)
    if abs(value) < 1e-6:
        print("Units: Likely microamps (uA) or nanoamps (nA) - CURRENT MODE")
    elif abs(value) < 1e-3:
        print("Units: Likely millivolts (mV) or milliamps (mA)")
    elif abs(value) < 1:
        print("Units: Likely volts (V) or amps (A)")
    else:
        print("Units: Unknown")
        
except Exception as e:
    print(f"Could not take reading: {e}")

print()
print("Check the 6487 front panel to see actual units displayed!")
print()

inst.close()
rm.close()
