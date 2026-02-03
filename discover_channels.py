"""
Discover all valid channels on Slot 1 (3721 card).
The 3721 is a Dual 1x20 Multiplexer:
  - Bank 1: 1001-1020
  - Bank 2: 1021-1040
"""
import pyvisa
import time

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
sw = rm.open_resource("GPIB0::16::INSTR")
sw.timeout = 5000

sw.write("errorqueue.clear()")
time.sleep(0.2)

print("Testing channels on Slot 1 (3721 Dual 1x20 Multiplexer)...")
print("=" * 60)

valid_channels = []

# Test Bank 1: 1001-1020
print("\nBank 1 (1001-1020):")
for ch in range(1001, 1021):
    sw.write("errorqueue.clear()")
    sw.write(f'channel.close("{ch}")')
    time.sleep(0.05)
    
    err = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in err or err.startswith("0"):
        valid_channels.append(ch)
        print(f"  {ch}: ✓ Valid")
        # Open it again
        sw.write(f'channel.open("{ch}")')
    else:
        print(f"  {ch}: ✗ Invalid ({err[:40]}...)")

# Test Bank 2: 1021-1040
print("\nBank 2 (1021-1040):")
for ch in range(1021, 1041):
    sw.write("errorqueue.clear()")
    sw.write(f'channel.close("{ch}")')
    time.sleep(0.05)
    
    err = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in err or err.startswith("0"):
        valid_channels.append(ch)
        print(f"  {ch}: ✓ Valid")
        # Open it again
        sw.write(f'channel.open("{ch}")')
    else:
        print(f"  {ch}: ✗ Invalid ({err[:40]}...)")

print("\n" + "=" * 60)
print(f"Found {len(valid_channels)} valid channels:")
print(valid_channels)

sw.close()
