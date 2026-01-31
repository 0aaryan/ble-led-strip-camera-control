BLE tools
=============

Quick scripts to scan, inspect and write to BLE devices using `bleak`.

Usage (from project root, in venv):

```bash
# scan for devices
env/bin/python scripts/ble_tools.py scan --timeout 5

# inspect a device (list services/characteristics)
env/bin/python scripts/ble_tools.py inspect --address AC:C2:01:39:3D:5D

# write to a specific characteristic
env/bin/python scripts/ble_tools.py write --address AC:C2:01:39:3D:5D --uuid 0000ffe1-0000-1000-8000-00805f9b34fb --hex 0a0b0c

# write to first writable characteristic (omit --uuid)
env/bin/python scripts/ble_tools.py write --address AC:C2:01:39:3D:5D --hex 0a0b0c
```

Notes:
- If `bleak` isn't installed in the project venv, install it:

```bash
env/bin/pip install bleak
```

- The `write` command will list available characteristics if the requested UUID is not found.
- The CLI is defensive and should work with older and newer `bleak` versions (uses `client.services` fallback).
