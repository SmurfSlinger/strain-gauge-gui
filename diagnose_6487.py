"""
Send each 6487 config command individually and check for errors after each one.
This tells us exactly which command generates the -113.
"""
import pyvisa
import time

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

pm = rm.open_resource("GPIB0::22::INSTR")
pm.timeout = 5000

# Start clean
pm.write("*CLS")
time.sleep(0.2)

commands = [
    "*IDN?",           # query
    "CONF:VOLT:DC",
    "VOLT:RANG:AUTO ON",
    "VOLT:NPLC 1",
    "FORM:ELEM READ",
]

for cmd in commands:
    # Clear before each command
    pm.write("*CLS")
    time.sleep(0.1)
    
    # Send command
    if cmd.endswith("?"):
        resp = pm.query(cmd).strip()
        print(f"  {cmd} -> {resp}")
    else:
        pm.write(cmd)
        print(f"  {cmd} -> sent")
    
    time.sleep(0.1)
    
    # Check error
    err = pm.query("SYST:ERR?").strip()
    if not (err.startswith("+0,") or err.startswith("0,")):
        print(f"    *** ERROR: {err}")
    else:
        print(f"    OK")

# Now test a READ
print("\n  Testing READ?...")
pm.write("*CLS")
time.sleep(0.1)
reading = pm.query("READ?").strip()
print(f"  READ? -> {reading}")
err = pm.query("SYST:ERR?").strip()
print(f"    Error check: {err}")

pm.close()
