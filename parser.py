"""
Ardra's Module: Parsing
Mobile OS Performance Analyzer

Converts raw ADB output into structured Python data.
"""

import re
from typing import Optional


def parse_number(value: str) -> Optional[float]:
    """Safely convert text into a float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_processes(raw_output: str) -> list[dict]:
    """
    Parse common Android ps output.

    Returns records using the team's shared format:
    pid, process, cpu_percent, memory_mb, threads
    """

    processes = []
    lines = raw_output.strip().splitlines()

    if not lines:
        return processes

    header_index = None
    headers = []

    for index, line in enumerate(lines):
        columns = line.split()
        if "PID" in columns and ("NAME" in columns or "CMD" in columns):
            header_index = index
            headers = columns
            break

    if header_index is None:
        return processes

    pid_index = headers.index("PID")
    name_index = headers.index("NAME") if "NAME" in headers else headers.index("CMD")
    rss_index = headers.index("RSS") if "RSS" in headers else None

    for line in lines[header_index + 1:]:
        columns = line.split()

        if len(columns) <= max(pid_index, name_index):
            continue

        try:
            pid = int(columns[pid_index])
        except ValueError:
            continue

        memory_mb = 0.0

        if rss_index is not None and len(columns) > rss_index:
            rss_kb = parse_number(columns[rss_index])
            if rss_kb is not None:
                memory_mb = round(rss_kb / 1024, 2)

        processes.append({
            "pid": pid,
            "process": columns[name_index],
            "cpu_percent": 0.0,
            "memory_mb": memory_mb,
            "threads": 0,
        })

    return processes


def parse_cpu_output(raw_output: str) -> dict[int, float]:
    """
    Parse CPU values from common Android top output.

    This parser uses the %CPU header when available.
    """

    cpu_data = {}
    lines = raw_output.strip().splitlines()

    header = None
    header_index = None

    for index, line in enumerate(lines):
        columns = line.split()
        if "%CPU" in columns and "PID" in columns:
            header = columns
            header_index = index
            break

    if header is None:
        return cpu_data

    pid_index = header.index("PID")
    cpu_index = header.index("%CPU")

    for line in lines[header_index + 1:]:
        columns = line.split()

        if len(columns) <= max(pid_index, cpu_index):
            continue

        try:
            pid = int(columns[pid_index])
            cpu = float(columns[cpu_index].replace("%", ""))
        except (ValueError, TypeError):
            continue

        cpu_data[pid] = cpu

    return cpu_data


def parse_thread_count(raw_output: str) -> Optional[int]:
    """Parse Threads from /proc/PID/status output."""
    match = re.search(r"^\s*Threads:\s*(\d+)", raw_output, re.MULTILINE)
    return int(match.group(1)) if match else None


def parse_memory_output(raw_output: str) -> dict:
    """Parse /proc/meminfo values and convert kB to MB."""
    memory = {}

    for line in raw_output.splitlines():
        match = re.match(r"^(\w+):\s+(\d+)\s+kB", line)
        if not match:
            continue

        key = match.group(1)
        value_kb = int(match.group(2))
        memory[key] = round(value_kb / 1024, 2)

    return memory


def parse_battery_output(raw_output: str) -> dict:
    """Parse dumpsys battery output."""
    battery = {}

    for line in raw_output.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key == "level":
            battery["battery_percent"] = int(value)
        elif key == "temperature":
            battery["temperature_c"] = int(value) / 10
        elif key == "AC powered":
            battery["ac_powered"] = value.lower() == "true"
        elif key == "USB powered":
            battery["usb_powered"] = value.lower() == "true"
        elif key == "status":
            battery["status"] = value

    return battery


def merge_process_data(
    processes: list[dict],
    cpu_data: dict[int, float],
) -> list[dict]:
    """Merge CPU values into process records."""
    for process in processes:
        pid = process["pid"]
        if pid in cpu_data:
            process["cpu_percent"] = cpu_data[pid]
    return processes


def build_process_data(
    process_output: str,
    cpu_output: str,
) -> list[dict]:
    """Build the shared process-data format."""
    processes = parse_processes(process_output)
    cpu_data = parse_cpu_output(cpu_output)
    return merge_process_data(processes, cpu_data)


if __name__ == "__main__":
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

    for record in build_process_data(sample_ps, sample_top):
        print(record)
