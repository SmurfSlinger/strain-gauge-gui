"""
diagnose.py - Instrument diagnostics and utilities.

Usage:
    python diagnose.py check      - Check error queues on all instruments
    python diagnose.py clear      - Clear error queues on all instruments
    python diagnose.py switch     - Test switch waitcomplete patterns (finding -104 fix)
    python diagnose.py 6487       - Test 6487 config commands one by one
    python diagnose.py all        - Run check, then clear, then both instrument tests
"""
import sys
import time
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

def get_switch():
    sw = rm.open_resource("GPIB0::16::INSTR")
    sw.timeout = 5000
    return sw

def get_6221():
    cs = rm.open_resource("GPIB0::12::INSTR")
    cs.timeout = 5000
    return cs

def get_6487():
    pm = rm.open_resource("GPIB0::22::INSTR")
    pm.timeout = 5000
    return pm

def switch_check_error(sw):
    err = sw.query("print(errorqueue.next())").strip()
    if "Queue Is Empty" in err:
        print("    OK")
    else:
        print(f"    *** ERROR: {err}")

# ─── check ────────────────────────────────────────────────────────
def cmd_check():
    print("=" * 60)
    print("CHECKING INSTRUMENT ERROR QUEUES")
    print("=" * 60)

    print("\n--- Switch 3700 (GPIB 16) ---")
    sw = get_switch()
    print(f"  IDN: {sw.query('*IDN?').strip()}")
    print("  Errors:")
    for _ in range(10):
        err = sw.query("print(errorqueue.next())").strip()
        if "Queue Is Empty" in err:
            print("    (empty)")
            break
        print(f"    {err}")
    sw.close()

    print("\n--- Current Source 6221 (GPIB 12) ---")
    cs = get_6221()
    print(f"  IDN: {cs.query('*IDN?').strip()}")
    print("  Errors:")
    for _ in range(10):
        err = cs.query("SYST:ERR?").strip()
        if err.startswith("+0,") or err.startswith("0,"):
            print("    (empty)")
            break
        print(f"    {err}")
    cs.close()

    print("\n--- Picoammeter 6487 (GPIB 22) ---")
    pm = get_6487()
    print(f"  IDN: {pm.query('*IDN?').strip()}")
    print("  Errors:")
    for _ in range(10):
        err = pm.query("SYST:ERR?").strip()
        if err.startswith("+0,") or err.startswith("0,"):
            print("    (empty)")
            break
        print(f"    {err}")
    pm.close()

# ─── clear ────────────────────────────────────────────────────────
def cmd_clear():
    print("=" * 60)
    print("CLEARING ERROR QUEUES")
    print("=" * 60)

    sw = get_switch()
    for _ in range(3):
        sw.write("errorqueue.clear()")
        time.sleep(0.1)
    print("  [OK] Switch 3700")
    sw.close()

    cs = get_6221()
    for _ in range(3):
        cs.write("*CLS")
        time.sleep(0.1)
    print("  [OK] Current Source 6221")
    cs.close()

    pm = get_6487()
    for _ in range(3):
        pm.write("*CLS")
        time.sleep(0.1)
    print("  [OK] Picoammeter 6487")
    pm.close()

# ─── switch ───────────────────────────────────────────────────────
def cmd_switch():
    print("=" * 60)
    print("SWITCH 3700 - Testing waitcomplete patterns")
    print("=" * 60)
    print("Looking for which pattern does NOT produce -104...\n")

    sw = get_switch()
    sw.write("errorqueue.clear()")
    time.sleep(0.2)

    # Pattern 1: current approach - separate writes
    print("Pattern 1: write(close) + write(waitcomplete)...")
    sw.write("channel.close(1002)")
    sw.write("waitcomplete()")
    switch_check_error(sw)
    sw.write("channel.open(1002)")
    sw.write("waitcomplete()")
    switch_check_error(sw)

    # Pattern 2: semicolon-combined single write
    print("\nPattern 2: write('close; waitcomplete')...")
    sw.write("channel.close(1002); waitcomplete()")
    switch_check_error(sw)
    sw.write("channel.open(1002); waitcomplete()")
    switch_check_error(sw)

    # Pattern 3: query print(waitcomplete()) to consume the return value
    print("\nPattern 3: write(close) + query(print(waitcomplete()))...")
    sw.write("channel.close(1002)")
    resp = sw.query("print(waitcomplete())").strip()
    print(f"    waitcomplete returned: {resp}")
    switch_check_error(sw)
    sw.write("channel.open(1002)")
    resp = sw.query("print(waitcomplete())").strip()
    print(f"    waitcomplete returned: {resp}")
    switch_check_error(sw)

    # Pattern 4: no waitcomplete, just a short sleep
    print("\nPattern 4: write(close) + sleep(100ms), no waitcomplete...")
    sw.write("channel.close(1002)")
    time.sleep(0.1)
    switch_check_error(sw)
    sw.write("channel.open(1002)")
    time.sleep(0.1)
    switch_check_error(sw)

    sw.close()

# ─── 6487 ─────────────────────────────────────────────────────────
def cmd_6487():
    print("=" * 60)
    print("PICOAMMETER 6487 - Testing config commands")
    print("=" * 60)
    print("Sending each command individually to find which ones are valid...\n")

    pm = get_6487()
    pm.write("*CLS")
    time.sleep(0.2)

    commands = [
        ("*IDN?", True),
        ("CONF:VOLT:DC", False),
        ("VOLT:RANG:AUTO ON", False),
        ("VOLT:NPLC 1", False),
        ("FORM:ELEM READ", False),
        ("SYST:MEAS:FUNC 'VOLT'", False),   # alternative config style
        ("MEAS:VOLT:DC?", True),             # alternative read style
    ]

    for cmd, is_query in commands:
        pm.write("*CLS")
        time.sleep(0.1)

        if is_query:
            try:
                resp = pm.query(cmd).strip()
                print(f"  {cmd} -> {resp}")
            except Exception as e:
                print(f"  {cmd} -> TIMEOUT/ERROR: {e}")
        else:
            pm.write(cmd)
            print(f"  {cmd} -> sent")

        time.sleep(0.1)
        err = pm.query("SYST:ERR?").strip()
        if err.startswith("+0,") or err.startswith("0,"):
            print(f"    OK")
        else:
            print(f"    *** ERROR: {err}")

    # Final READ test
    print("\n  Final READ? test...")
    pm.write("*CLS")
    time.sleep(0.1)
    try:
        reading = pm.query("READ?").strip()
        print(f"  READ? -> {reading}")
    except Exception as e:
        print(f"  READ? -> TIMEOUT: {e}")

    pm.close()

# ─── main ─────────────────────────────────────────────────────────
commands = {
    "check":  cmd_check,
    "clear":  cmd_clear,
    "switch": cmd_switch,
    "6487":   cmd_6487,
    "all":    lambda: (cmd_check(), cmd_clear(), cmd_switch(), cmd_6487()),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(__doc__)
        sys.exit(1)
    commands[sys.argv[1]]()
