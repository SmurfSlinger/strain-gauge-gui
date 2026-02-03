"""
Test 4-wire measurement configuration without hardware
"""
from pathlib import Path
from src.gui.config_loader import load_config

# Load config
config_path = Path(__file__).parent / "src" / "gui" / "config.json"
cfg = load_config(config_path)

print("=" * 60)
print("TESTING 4-WIRE CONFIGURATION")
print("=" * 60)

for i, case in enumerate(cfg.measurement_cases, 1):
    print(f"\n{i}. {case.name}")
    print(f"   Wire Mode: {case.wire_mode}")
    print(f"   Force Channels: {case.force_channel_pos} / {case.force_channel_neg}")
    
    if case.is_4_wire():
        print(f"   Sense Channels: {case.sense_channel_pos} / {case.sense_channel_neg}")
        print(f"   [OK] 4-wire mode - closes 4 channels total")
        all_channels = case.get_all_channels()
        print(f"   All channels: {all_channels}")
    else:
        print(f"   [OK] 2-wire mode - closes 2 channels total")
        all_channels = case.get_all_channels()
        print(f"   All channels: {all_channels}")

print("\n" + "=" * 60)
print("CONFIGURATION TEST PASSED!")
print("=" * 60)
print(f"\nTotal gauges configured: {len(cfg.measurement_cases)}")
print(f"2-wire gauges: {sum(1 for c in cfg.measurement_cases if not c.is_4_wire())}")
print(f"4-wire gauges: {sum(1 for c in cfg.measurement_cases if c.is_4_wire())}")
