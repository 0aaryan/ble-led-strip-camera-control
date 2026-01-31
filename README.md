# LED Strip Control Dashboard

A modern web-based dashboard for controlling Bluetooth LE LED strips with camera-based brightness detection.

## ✨ Features

- 📡 **BLE Device Scanner**: Discover and connect to nearby Bluetooth devices
- 🔌 **Connection Testing**: Verify LED strip connectivity and status
- 💡 **LED Control Panel**: Control LED colors with quick presets or custom commands
- 📹 **Camera Monitoring**: Real-time brightness detection using your webcam
- 🎨 **Modern UI**: Responsive dashboard with gradient backgrounds and smooth animations
- ⚡ **Real-time Updates**: Live status information and system feedback

## 🏗️ Project Structure

```
ble-led-strip-camera-control/
├── core/                    # Backend Python modules
│   ├── server.py           # FastAPI server with REST API
│   ├── ble_test.py         # BLE utilities (CLI)
│   ├── camera_detect.py    # Camera monitoring (CLI)
│   └── main.py             # CLI entry point
├── web/static/             # Frontend files
│   ├── index.html          # Landing page
│   └── dashboard.html      # Main dashboard
├── docs/                   # Documentation
│   ├── API.md              # API reference
│   └── ARCHITECTURE.md     # System design
├── config/                 # Configuration (future use)
├── tests/                  # Tests (future use)
└── pyproject.toml          # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Bluetooth adapter (built-in or USB)
- Webcam (for camera monitoring features)

### Installation

1. **Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Clone the repository**:
```bash
git clone https://github.com/0aaryan/ble-led-strip-camera-control.git
cd ble-led-strip-camera-control
```

3. **Install dependencies**:
```bash
poetry install
```

### Running the Dashboard

Start the web server:
```bash
poetry run python -m core.server
```

Then open your browser and navigate to:
```
http://127.0.0.1:8000
```

### Using the Dashboard

1. **Scan for Devices**: Click "Scan for Devices" to discover nearby BLE devices
2. **Select Device**: Click "Select" on your LED strip device
3. **Test Connection**: The dashboard automatically tests the connection
4. **Control LEDs**: Use the color picker or send custom hex commands
5. **Monitor Brightness**: Start camera preview and monitoring to detect LED changes

## 🖥️ CLI Mode

You can also use the command-line interface for testing:

### Scan for BLE Devices
```bash
poetry run python -m core.main ble scan --timeout 5
```

### Inspect a Device
```bash
poetry run python -m core.main ble inspect --address AA:BB:CC:DD:EE:FF
```

### Send Command to LED
```bash
poetry run python -m core.main ble write \
  --address AA:BB:CC:DD:EE:FF \
  --uuid 0000fff3-0000-1000-8000-00805f9b34fb \
  --hex ff0000
```

### Monitor Camera (OpenCV)
```bash
poetry run python -m core.main camera --device 0 --threshold 15
```

## 📡 API Endpoints

See [API Documentation](docs/API.md) for complete API reference.

**Quick Reference:**
- `GET /api/scan?timeout=5.0` - Scan for BLE devices
- `GET /api/inspect?address=...` - Inspect device services
- `GET /api/test-connection?address=...` - Test device connection
- `POST /api/led/write` - Send command to LED strip

## 🎨 LED Color Commands

Most LED strips accept 3-byte RGB hex values:

| Color   | Hex Code |
|---------|----------|
| Red     | `ff0000` |
| Green   | `00ff00` |
| Blue    | `0000ff` |
| White   | `ffffff` |
| Yellow  | `ffff00` |
| Cyan    | `00ffff` |
| Magenta | `ff00ff` |
| Off     | `000000` |

**Note**: The exact command format depends on your LED strip model. The default UUID `0000fff3-0000-1000-8000-00805f9b34fb` works with many common BLE LED strips.

## 🔧 Configuration

### Finding Your LED Strip's UUID

1. Run the dashboard and scan for your device
2. Select your device and click "Inspect Services"
3. Look for characteristics with "write" property
4. Common LED control UUIDs:
   - `0000fff3-0000-1000-8000-00805f9b34fb` (most common)
   - `0000ffe1-0000-1000-8000-00805f9b34fb`
   - Check your LED strip's documentation

## 🐛 Troubleshooting

### Bluetooth Issues
- **Linux**: Ensure BlueZ 5.43+ is installed. You may need to run with `sudo` or set capabilities:
  ```bash
  sudo setcap cap_net_raw+ep $(readlink -f $(which python))
  ```
- **macOS**: Bluetooth should work out of the box
- **Windows**: Ensure Bluetooth is enabled in system settings

### Camera Issues
- Grant camera permissions when prompted by your browser
- Check that no other application is using the camera
- Try a different browser if camera enumeration fails

### Connection Failures
- Ensure the LED strip is powered on
- Move closer to the device (RSSI > -70 is ideal)
- Check that the device isn't already connected to another app
- Some devices can only maintain one connection at a time

## 📚 Documentation

- [API Reference](docs/API.md) - Complete API documentation
- [Architecture](docs/ARCHITECTURE.md) - System design and technical details

## 🛠️ Development

### Running Tests
```bash
poetry run pytest tests/
```

### Code Style
This project follows standard Python conventions (PEP 8). Format with:
```bash
python3 -m black core/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📝 License

This project is provided as-is for educational and personal use.

## 🎯 Next Steps

Planned features:
- [ ] WebSocket support for real-time updates
- [ ] Persistent device pairing and configuration
- [ ] Advanced LED pattern presets (rainbow, fade, strobe)
- [ ] Image capture when brightness changes detected
- [ ] Multi-device support
- [ ] React-based frontend with build tooling
- [ ] User authentication and session management
- [ ] Database for logging and history

