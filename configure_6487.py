"""
Configure the 6487 Picoammeter for voltage measurements
"""
import pyvisa

rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")

print("Configuring 6487 Picoammeter...")

pm = rm.open_resource("GPIB0::22::INSTR")
pm.timeout = 5000

print(f"IDN: {pm.query('*IDN?').strip()}")

# Reset to known state
pm.write("*RST")
print("  Reset instrument")

# Clear errors
pm.write("*CLS")

# Configure for voltage measurement
pm.write("CONF:VOLT:DC")  # Configure for DC voltage measurement
print("  Configured for DC voltage measurement")

# Set voltage range (auto)
pm.write("VOLT:RANG:AUTO ON")
print("  Auto-ranging enabled")

# Set integration time (faster measurements)
pm.write("VOLT:NPLC 1")  # 1 power line cycle
print("  Integration time set to 1 PLC")

# Configure measurement format
pm.write("FORM:ELEM READ")  # Only return reading value
print("  Format set to reading only")

# Test a reading
print("\nTesting measurement...")
try:
    reading = pm.query("READ?").strip()
    print(f"  Voltage reading: {reading} V")
    print("  SUCCESS!")
except Exception as e:
    print(f"  FAILED: {e}")

# Check for errors
err = pm.query("SYST:ERR?").strip()
print(f"\nError check: {err}")

pm.close()
print("\nDone! 6487 is configured.")
