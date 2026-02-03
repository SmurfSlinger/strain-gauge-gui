"""
Test different channel number formats and operations to find what works without -104.
"""
import pyvisa
import time

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
sw = rm.open_resource("GPIB0::16::INSTR")
sw.timeout = 5000

def check():
    err = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in err or err.startswith("0"):
        print("    ✓ OK")
    else:
        print(f"    ✗ ERROR: {err}")

sw.write("errorqueue.clear()")
time.sleep(0.2)

# First, let's see what slots are actually installed
print("=== Checking installed slots ===")
for slot in range(1, 7):
    try:
        installed = sw.query(f"print(slot[{slot}].idn)").strip()
        if installed and installed != "nil":
            print(f"Slot {slot}: {installed}")
    except:
        pass

print("\n=== Testing channel operations ===")

# Test 1: Try the exact format from your old test.py that worked
print("\nTest 1: Using quoted string '1002'...")
sw.write('channel.close("1002")')
check()
sw.write('channel.open("1002")')  
check()

# Test 2: Different channel (slot 2, channel 1)
print("\nTest 2: Using channel 2001 (slot 2, ch 1)...")
sw.write("channel.close(2001)")
check()
sw.write("channel.open(2001)")
check()

# Test 3: Check if getstate works
print("\nTest 3: Checking channel.getstate(1002)...")
state = sw.query("print(channel.getstate(1002))").strip()
print(f"    State: {state}")
check()

# Test 4: Check if the channel list exists
print("\nTest 4: Checking channel.getclose()...")
try:
    closed = sw.query("print(channel.getclose())").strip()
    print(f"    Currently closed: {closed}")
except Exception as e:
    print(f"    Error: {e}")
check()

sw.close()
