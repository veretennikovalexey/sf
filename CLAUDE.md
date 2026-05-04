# Project: Python clone of SkanerF

A Python console application that listens on a COM port and prints data received from a barcode scanner (the scanner is configured in COM-port emulation mode, not keyboard mode).

The user is Russian-speaking. All user-facing output (console messages, README, error text) MUST be in Russian. This file (CLAUDE.md) is internal context for Claude and is in English.

## Port parameters (defaults, mirroring SkanerF)

- Port: COM6
- Baud rate: 9600
- Data bits: 8
- Parity: none (N)
- Stop bits: 1

## Implementation decisions

### 1. Scan-end suffix
**CR (`\r`)** — try this first. If it doesn't work, adjust later (try `\n`, `\r\n`, or read by timeout).

### 2. Source of the COM port name
Read from the existing `SkanerF.ini` file (the same file used by `SkanerF.exe` — DO NOT delete or overwrite it).

From the ini we read only the `ComPort` parameter from the `[Nastr]` section:

```
[Nastr]
ComPort=COM6
```

The other ini parameters (Baud, Parity, StopBits, ByteSize) are **not read** — they're in SkanerF's own format and not needed here. Speed/bits/parity/stop bits are hardcoded in Python (9600, 8, N, 1).

### 3. Behaviour when the COM port is busy
**Print an error and exit.** Message like: `Не удалось открыть COM6: порт занят. Закройте SkanerF.exe и попробуйте снова.`

### 4. What to do with received data
**Print to console + append to a file** (append mode, no overwriting).

### 5. Output file for scans
- **Filename:** `SkanerF.txt` (the same filename `SkanerF.exe` uses).
- **Location:** the current working directory of the Python script (do NOT read the path from the ini — always write to the cwd).
- **Mode:** create if missing, append if exists (`'a'` mode).
- **Line format:** `2026-05-04 14:23:11 | 1234567890` (date/time + barcode).
- **Encoding:** UTF-8 (the existing `SkanerF.txt` is ASCII, which is a subset of UTF-8 — fully compatible).
- **Single shared file for both `SkanerF.exe` and the Python version.** Scan histories are concatenated (user confirmed this is fine).

### 6. Stopping the program
Via `Ctrl+C` (the standard way). The script catches `KeyboardInterrupt`, closes the port cleanly, and exits.

### 7. Encoding of data from the scanner
**UTF-8** (read bytes, decode as UTF-8). If barcodes contain only digits / Latin characters, encoding is irrelevant — UTF-8 is universal.

## Project files

- `SkanerF.exe` — the original program (do not touch).
- `SkanerF.ini` — config (read `ComPort`, do not modify).
- `SkanerF.txt` — scan history (shared with the .exe, append mode).
- `scanner.py` — our Python program.
- `README.md` — Russian-language user instructions.
- `CLAUDE.md` — this file, project context for Claude.
- `.gitignore` — excludes `__pycache__/`, `*.pyc`, `test_out.txt`, `SkanerF.txt`.

## Dependencies
- Python 3.x
- `pyserial` (install: `pip install pyserial`)

## Repository
- GitHub: https://github.com/veretennikovalexey/sf
