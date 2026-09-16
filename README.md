# Ardra: ADB + Data Collection + Parsing

## Files

- `adb_collector.py`: Connects to Android through ADB and collects raw data.
- `parser.py`: Converts raw ADB output into structured process records.
- `test_ardra_module.py`: Tests the parser and checks ADB connection.

## Required process data format

```python
{
    "pid": 1023,
    "process": "SystemUI",
    "cpu_percent": 3.5,
    "memory_mb": 180.0,
    "threads": 42
}
```

## Setup

1. Install Android SDK Platform Tools.
2. Add `adb` to PATH.
3. Enable Developer Options and USB Debugging on your phone.
4. Connect the phone.
5. Accept the USB debugging prompt.
6. Open terminal in this folder.

## Run

```bash
adb devices
python adb_collector.py
python parser.py
python test_ardra_module.py
```

## Important

Android versions expose different `ps` and `top` column formats. Check your actual phone output and adjust the parser if needed. Thread counts may require reading `/proc/<PID>/status`, and Android permissions can restrict access.
