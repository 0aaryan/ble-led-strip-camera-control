# LED Strip Control Dashboard

A modern web-based dashboard for controlling Bluetooth LE LED strips with camera-based brightness detection. **Now with ELK-BLEDOM protocol support** for color-changing LED strips compatible with the "com.ledlamp" Android app.

## ✨ Features

- 📡 **BLE Device Scanner**: Discover and connect to nearby Bluetooth devices
- 🔌 **Connection Testing**: Verify LED strip connectivity and status
- 💡 **LED Control Panel**: Control LED colors with 12 vibrant gradient presets or custom commands
- 🎨 **ELK-BLEDOM Protocol Support**: Full compatibility with color-changing LED strips
- 📹 **Camera Monitoring**: Real-time brightness detection using your webcam
- ✨ **Modern UI**: Responsive dashboard with gradient backgrounds, smooth animations, and enhanced button effects
- ⚡ **Real-time Updates**: Live status information and system feedback
- 🌐 **Offline-First**: No external CDN dependencies, works completely offline

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

This application supports the **ELK-BLEDOM protocol**, which is used by many BLE LED strips controlled by apps like "com.ledlamp" (LED LAMP).

### Protocol Format

Commands follow this 10-byte structure:
```
[0x7e, 0x07, 0x05, 0x03, RR, GG, BB, 0x00, 0x00, 0xef]
```

- **Header**: `0x7e 0x07 0x05 0x03` - Command prefix
- **RR**: Red value (0x00-0xFF)
- **GG**: Green value (0x00-0xFF)
- **BB**: Blue value (0x00-0xFF)
- **Padding**: `0x00 0x00` - Reserved bytes
- **Footer**: `0xef` - Command terminator

### Color Examples

| Color   | RGB Hex | Full Command                    |
|---------|---------|--------------------------------|
| Red     | `ff0000` | `7e070503ff00000000ef`         |
| Green   | `00ff00` | `7e07050300ff000000ef`         |
| Blue    | `0000ff` | `7e0705030000ff0000ef`         |
| Yellow  | `ffff00` | `7e070503ffff000000ef`         |
| Cyan    | `00ffff` | `7e07050300ffff0000ef`         |
| Magenta | `ff00ff` | `7e070503ff00ff0000ef`         |
| Orange  | `ff8800` | `7e070503ff88000000ef`         |
| Purple  | `8800ff` | `7e0705038800ff0000ef`         |
| Pink    | `ff1493` | `7e070503ff14930000ef`         |
| White   | `ffffff` | `7e070503ffffff0000ef`         |
| Off     | `000000` | `7e0705030000000000ef`         |

### Characteristic UUID

The default write characteristic UUID for ELK-BLEDOM compatible LED strips is:
```
0000ffe1-0000-1000-8000-00805f9b34fb
```

Alternative UUIDs (less common):
- `0000fff3-0000-1000-8000-00805f9b34fb`

**Note**: Use the "Inspect Services" feature in the dashboard to verify your device's correct UUID.

## 🔧 Configuration

### Supported LED Strips

This dashboard is designed to work with **ELK-BLEDOM** compatible LED strips, including:
- Strips controlled by the "com.ledlamp" Android app
- Generic BLE LED strips from Flipkart, Amazon, etc.
- Any LED strip using the ELK-BLEDOM protocol

### Finding Your LED Strip's UUID

1. Run the dashboard and scan for your device
2. Select your device and click "Inspect Services"
3. Look for characteristics with "write" property
4. Common LED control UUIDs:
   - `0000ffe1-0000-1000-8000-00805f9b34fb` (ELK-BLEDOM standard)
   - `0000fff3-0000-1000-8000-00805f9b34fb` (alternative)
   - Check your LED strip's documentation if neither works

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

