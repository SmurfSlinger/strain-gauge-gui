"""
Send each switch command individually and check for errors after each one.
This tells us exactly which command generates the -104.
Simulates what happens when you press Record:
  open_all() -> close_channel(1002) -> close_channel(1002)
"""
import pyvisa
import time

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

sw = rm.open_resource("GPIB0::16::INSTR")
sw.timeout = 5000

def check_error():
    err = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in err:
        print("    OK")
    else:
        print(f"    *** ERROR: {err}")

# Start clean
sw.write("errorqueue.clear()")
time.sleep(0.2)

# Step 1: open_all() with nothing previously closed (empty set)
# This is what happens first time you press record
print("Step 1: open_all() with nothing closed (no-op, should do nothing)...")
# In your code, open_all iterates closed_channels which is empty,
# so nothing actually gets sent. But let's confirm the switch is clean:
check_error()

# Step 2: close channel 1002 (first force channel)
print("Step 2: channel.close(1002)...")
sw.write("channel.close(1002)")
sw.write("waitcomplete()")
check_error()

# Step 3: close channel 1002 again (second force channel, same as first)
print("Step 3: channel.close(1002) again (already closed)...")
sw.write("channel.close(1002)")
sw.write("waitcomplete()")
check_error()

# Step 4: Now simulate stop -> open_all() opens what we closed
print("Step 4: channel.open(1002)...")
sw.write("channel.open(1002)")
sw.write("waitcomplete()")
check_error()

# Step 5: open it again (already open)
print("Step 5: channel.open(1002) again (already open)...")
sw.write("channel.open(1002)")
sw.write("waitcomplete()")
check_error()

sw.close()
