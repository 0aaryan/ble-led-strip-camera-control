LED Strip Helper
=================

Overview
--------
This project provides two interfaces to test and control LED strip hardware (commonly controlled via Bluetooth):

- CLI tools (in `core/`) for BLE scanning, inspection and simple write operations.
- Browser UI (single-page app in `web/static/`) that talks to a Python backend and uses your laptop's camera from the browser to monitor brightness.

Design decisions
----------------
- BLE access and any hardware-level operations run in Python using `bleak`. This avoids browser BLE limitations for some platforms and provides stable access to local adapters.
- Camera detection for the UI is performed client-side in the browser using `getUserMedia` and canvas sampling (no OpenCV required for the UI). This simplifies permissions and makes the UI fast.
- The backend is a small FastAPI app that exposes BLE scan/inspect endpoints and serves the UI static files. This makes it easy to keep CLI mode and UI mode in the same project.

Project structure
-----------------
- `core/ble_test.py` - CLI BLE helper (scan/inspect/write)
- `core/camera_detect.py` - (optional) OpenCV camera-based monitor (CLI)
- `core/main.py` - CLI wrapper to call BLE and camera helpers
- `core/server.py` - FastAPI server exposing `/api/scan` and `/api/inspect` and serving the static UI
- `web/static/index.html` - Single-page UI (landing -> scan -> choose device -> choose camera)
- `README.md` - This file

Requirements
------------
We recommend using Poetry for a clean environment.

1. Install Poetry (if not installed):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Create the virtual environment and install Python deps:

```bash
poetry init --no-interaction
poetry add fastapi uvicorn[standard] bleak
# If you want to use the OpenCV CLI monitor (optional):
poetry add opencv-python
```

If you prefer to use the existing `pyproject.toml`, add the dependencies there and run `poetry install`.

Running the CLI
----------------
You can run BLE and camera CLI helpers from `core/main.py` (they are lazy-imported so dependencies are only required when used):

```bash
# Scan BLE devices
poetry run python -m core.main ble scan --timeout 5

# Inspect a device (replace ADDRESS)
poetry run python -m core.main ble inspect --address AC:C2:01:39:3D:5D

# Use the OpenCV camera-based monitor (optional)
poetry run python -m core.main camera --device 0 --threshold 15
```

Running the UI
--------------
Start the FastAPI server and open the UI in your browser:

```bash
poetry run python -m core.server
# Visit http://127.0.0.1:8000/ in your browser
```

UI Flow (what the app does)
---------------------------
1. Landing page with two buttons: "Scan Bluetooth Devices" and "Choose Camera".
2. "Scan" calls `/api/scan` and lists discovered devices. Select a device to proceed.
3. Camera page enumerates available cameras via `navigator.mediaDevices` and previews the selected camera.
4. Start monitoring: the client captures a baseline brightness and detects changes; detected changes are logged and can be extended to call backend APIs or save images.

Why this architecture is a good fit
----------------------------------
- Using a Python backend for BLE avoids differences between browsers and OS-level BLE implementations.
- Client-side camera handling avoids heavy native deps and lets the user grant camera permission directly in the browser.
- The stack is lightweight and easy to package: most work is in Python + simple static frontend.

Next steps you can ask me to implement
-------------------------------------
- Add a persistent configuration and pairing flow (store chosen device UUIDs).
- Add BLE write/command UI to send control packets to the LED strip.
- Implement Server-Sent Events (SSE) or WebSocket from server to browser for real-time notifications.
- Capture and upload snapshot images when brightness changes.
- Wrap frontend in a proper SPA framework (React/Vue) and add build tooling.

If you'd like, I can now:
- Add BLE write UI so you can send commands to the selected device.
- Add pairing and persistent settings.
- Convert the UI to React + Vite and add a `package.json`.

Tell me which next step you'd prefer and I'll implement it.
