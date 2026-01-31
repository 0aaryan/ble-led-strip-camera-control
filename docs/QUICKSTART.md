# Quick Start Guide

This guide will help you get started with the LED Strip Control Dashboard in minutes.

## Prerequisites

Before you begin, ensure you have:
- Python 3.10 or higher installed
- A Bluetooth adapter (built-in or USB dongle)
- A BLE LED strip device
- (Optional) A webcam for camera monitoring

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/0aaryan/ble-led-strip-camera-control.git
cd ble-led-strip-camera-control
```

### 2. Install Dependencies

You can use either pip or Poetry:

**Using pip:**
```bash
pip3 install fastapi 'uvicorn[standard]' bleak numpy opencv-python
```

**Using Poetry:**
```bash
poetry install
```

### 3. Start the Server
```bash
python3 -m core.server
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 4. Open the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

## Using the Dashboard

### Step 1: Scan for BLE Devices
1. Click the **"Scan for Devices"** button
2. Wait 4-5 seconds for the scan to complete
3. You'll see a list of discovered Bluetooth devices

### Step 2: Select Your LED Strip
1. Find your LED strip in the list (look for familiar names or MAC addresses)
2. Click the **"Select"** button next to your device
3. The system will automatically test the connection

### Step 3: Control Your LED Strip

Once connected, you can:

**Use Quick Colors:**
- Click any color button to instantly change your LED strip color
- Available presets: Red, Green, Blue, Yellow, Magenta, Cyan, White, Off

**Send Custom Commands:**
- Enter a characteristic UUID (default is pre-filled for common LED strips)
- Enter hex data (e.g., `ff0000` for red, `00ff00` for green)
- Click **"Send Command"**

### Step 4: Monitor Brightness (Optional)

To use camera-based brightness detection:

1. **Select Camera:**
   - Choose your camera from the dropdown
   - Click **"Start Preview"** to see the camera feed

2. **Configure Monitoring:**
   - Set the brightness threshold (default: 15)
   - Click **"Start Monitoring"**

3. **View Results:**
   - The system captures a baseline brightness
   - Changes beyond the threshold are logged in the console
   - Current brightness is displayed in real-time

## Common LED Strip UUIDs

Most LED strips use one of these characteristic UUIDs:
- `0000fff3-0000-1000-8000-00805f9b34fb` (most common)
- `0000ffe1-0000-1000-8000-00805f9b34fb` (alternative)

You can find your device's UUID by clicking **"Inspect Services"**.

## Color Command Reference

| Color   | Hex Code | Description |
|---------|----------|-------------|
| Red     | `ff0000` | Pure red    |
| Green   | `00ff00` | Pure green  |
| Blue    | `0000ff` | Pure blue   |
| Yellow  | `ffff00` | Red + Green |
| Cyan    | `00ffff` | Green + Blue |
| Magenta | `ff00ff` | Red + Blue  |
| White   | `ffffff` | All colors  |
| Off     | `000000` | LEDs off    |

## CLI Mode (Advanced)

You can also use command-line tools:

**Scan for devices:**
```bash
python3 -m core.main ble scan --timeout 5
```

**Inspect a device:**
```bash
python3 -m core.main ble inspect --address AA:BB:CC:DD:EE:FF
```

**Send a command:**
```bash
python3 -m core.main ble write \
  --address AA:BB:CC:DD:EE:FF \
  --uuid 0000fff3-0000-1000-8000-00805f9b34fb \
  --hex ff0000
```

**Monitor camera (OpenCV):**
```bash
python3 -m core.main camera --device 0 --threshold 15
```

## Troubleshooting

### "No devices found"
- Ensure Bluetooth is enabled on your computer
- Make sure your LED strip is powered on
- Try moving closer to the LED strip
- On Linux, you may need to run with `sudo`

### Connection fails
- Check that the device isn't already connected to another app
- Some devices only allow one connection at a time
- Verify the device address is correct

### Camera not working
- Grant camera permissions when your browser prompts
- Ensure no other app is using the camera
- Try a different browser (Chrome/Firefox recommended)

### Linux Bluetooth Permission Issues
```bash
# Grant capabilities to Python
sudo setcap cap_net_raw+ep $(readlink -f $(which python3))

# Or run with sudo (less secure)
sudo python3 -m core.server
```

## Next Steps

- Check out the [API Documentation](API.md) for programmatic access
- Read the [Architecture Overview](ARCHITECTURE.md) to understand the system design
- Contribute improvements via pull requests!

## Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Look at the System Information panel in the dashboard
3. Review the troubleshooting section above
4. Open an issue on GitHub with detailed information

Happy controlling! 🎨💡
