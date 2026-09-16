"""
Ardra's Module: ADB + Data Collection
Mobile OS Performance Analyzer

Collects raw Android process, CPU, memory, thread, and battery data.
"""

import shutil
import subprocess
from typing import Optional


class ADBError(Exception):
    """Raised when an ADB command fails."""
    pass


def run_adb_command(args: list[str], timeout: int = 10) -> str:
    """Run an ADB command and return its raw output."""

    if shutil.which("adb") is None:
        raise ADBError(
            "ADB was not found. Install Android SDK Platform Tools "
            "and add adb to your PATH."
        )

    try:
        result = subprocess.run(
            ["adb"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ADBError(f"ADB command timed out after {timeout} seconds.")
    except OSError as error:
        raise ADBError(f"Could not run ADB: {error}")

    if result.returncode != 0:
        raise ADBError(result.stderr.strip() or "ADB command failed.")

    return result.stdout


def get_device_list() -> list[dict]:
    """Return connected Android devices and their statuses."""
    output = run_adb_command(["devices"])
    devices = []

    for line in output.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append({
                "device_id": parts[0],
                "status": parts[1],
            })

    return devices


def check_device() -> bool:
    """Return True when at least one authorized device is connected."""
    return any(
        device["status"] == "device"
        for device in get_device_list()
    )


def get_processes_raw() -> str:
    """Collect raw running process information."""
    return run_adb_command(["shell", "ps"], timeout=15)


def get_cpu_raw() -> str:
    """Collect one CPU usage snapshot."""
    return run_adb_command(["shell", "top", "-n", "1"], timeout=15)


def get_memory_raw() -> str:
    """Collect overall Android memory information."""
    return run_adb_command(["shell", "cat", "/proc/meminfo"], timeout=10)


def get_battery_raw() -> str:
    """Collect raw battery information."""
    return run_adb_command(["shell", "dumpsys", "battery"], timeout=10)


def get_threads_raw(pid: int) -> str:
    """Collect raw thread information for one process."""
    return run_adb_command(
        ["shell", "cat", f"/proc/{int(pid)}/status"],
        timeout=10,
    )


def collect_raw_data() -> dict:
    """Collect raw process, CPU, memory, and battery data."""
    if not check_device():
        raise ADBError(
            "No authorized Android device found. "
            "Enable USB debugging and accept the authorization prompt."
        )

    return {
        "processes": get_processes_raw(),
        "cpu": get_cpu_raw(),
        "memory": get_memory_raw(),
        "battery": get_battery_raw(),
    }


if __name__ == "__main__":
    print("Checking Android device connection...")

    try:
        devices = get_device_list()

        if not devices:
            print("No Android devices found.")
        else:
            for device in devices:
                print(
                    f"Device: {device['device_id']} | "
                    f"Status: {device['status']}"
                )

        if check_device():
            print("\nADB connection successful.")
            print("\nRunning processes:")
            print(get_processes_raw()[:1500])

            print("\nCPU information:")
            print(get_cpu_raw()[:1500])

            print("\nMemory information:")
            print(get_memory_raw()[:1500])

            print("\nBattery information:")
            print(get_battery_raw())
        else:
            print("\nNo authorized device. Check USB debugging.")

    except ADBError as error:
        print(f"\nADB Error: {error}")
