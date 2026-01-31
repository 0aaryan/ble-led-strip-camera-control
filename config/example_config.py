# Configuration Example

# This file shows example configuration options for the LED Strip Control system.
# Copy this to config/settings.py and customize as needed.

# Default BLE scan timeout in seconds
DEFAULT_SCAN_TIMEOUT = 5.0

# Default camera brightness threshold (0-255)
DEFAULT_BRIGHTNESS_THRESHOLD = 15

# Common LED strip characteristic UUIDs
LED_CHAR_UUIDS = [
    "0000fff3-0000-1000-8000-00805f9b34fb",  # Most common
    "0000ffe1-0000-1000-8000-00805f9b34fb",  # Alternative
]

# Server configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

# Camera settings
CAMERA_DEVICE_ID = 0
CAMERA_BASELINE_FRAMES = 20
CAMERA_MONITOR_INTERVAL_MS = 150

# Saved devices (example - would be stored in a database in production)
SAVED_DEVICES = {
    # "device_id": {
    #     "name": "My LED Strip",
    #     "address": "AA:BB:CC:DD:EE:FF",
    #     "uuid": "0000fff3-0000-1000-8000-00805f9b34fb"
    # }
}
