"""
Test file for Ardra's ADB collector and parser module.
Run:
    python test_ardra_module.py
"""

from adb_collector import ADBError, get_device_list, check_device
from parser import build_process_data, parse_memory_output, parse_battery_output


def test_parser():
    sample_ps = """
USER       PID   PPID  VSZ    RSS   WCHAN  ADDR S NAME
system     845   1     50000  18000 ...    ...  S system_server
u0_a123    2201  845   80000  41000 ...    ...  S com.android.chrome
"""

    sample_top = """
PID USER      PR  NI VIRT RES SHR S %CPU %MEM TIME+ NAME
845 system    10  0  50000 18000 0 S 4.1 2.0 00:01 system_server
2201 u0_a123  10  0  80000 41000 0 S 8.1 5.0 00:02 com.android.chrome
"""

    records = build_process_data(sample_ps, sample_top)

    assert len(records) == 2
    assert records[0]["pid"] == 845
    assert records[1]["cpu_percent"] == 8.1
    print("Parser test passed.")


def test_memory():
    memory = parse_memory_output("MemTotal:       8192000 kB\nMemAvailable:   4096000 kB")
    assert memory["MemTotal"] == 8000.0
    assert memory["MemAvailable"] == 4000.0
    print("Memory parser test passed.")


def test_battery():
    battery = parse_battery_output("level: 76\ntemperature: 320\nUSB powered: true")
    assert battery["battery_percent"] == 76
    assert battery["temperature_c"] == 32.0
    assert battery["usb_powered"] is True
    print("Battery parser test passed.")


if __name__ == "__main__":
    test_parser()
    test_memory()
    test_battery()

    try:
        print("\nADB devices:")
        print(get_device_list())
        print("Authorized device connected:", check_device())
    except ADBError as error:
        print("ADB test skipped or failed:", error)
