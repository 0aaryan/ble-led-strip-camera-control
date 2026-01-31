# Architecture Overview

## Project Structure

```
ble-led-strip-camera-control/
├── core/                    # Backend Python modules
│   ├── __init__.py
│   ├── server.py           # FastAPI server with BLE endpoints
│   ├── ble_test.py         # BLE utilities (scan/inspect/write)
│   ├── camera_detect.py    # OpenCV camera monitoring (CLI)
│   └── main.py             # CLI entry point
├── web/                     # Frontend assets
│   └── static/
│       ├── index.html      # Landing page
│       └── dashboard.html  # Main dashboard UI
├── docs/                    # Documentation
│   ├── API.md              # API documentation
│   └── ARCHITECTURE.md     # This file
├── config/                  # Configuration files (future use)
├── tests/                   # Test files (future use)
├── pyproject.toml          # Python dependencies
├── poetry.lock             # Locked dependencies
└── README.md               # Project overview
```

## System Architecture

### Backend (Python + FastAPI)

The backend is built with FastAPI and provides:

1. **BLE Communication** - Using `bleak` library for cross-platform Bluetooth LE support
2. **REST API** - Endpoints for device scanning, inspection, connection testing, and LED control
3. **Static File Serving** - Serves the frontend dashboard

**Key Components:**

- **server.py**: Main FastAPI application with all API endpoints
- **ble_test.py**: Low-level BLE utilities (can be used standalone via CLI)
- **camera_detect.py**: OpenCV-based brightness monitoring (CLI mode)
- **main.py**: CLI wrapper for running tools independently

### Frontend (HTML/CSS/JavaScript)

The frontend is a single-page application built with vanilla JavaScript:

1. **Landing Page** - Feature overview and entry point
2. **Dashboard** - Main control interface with:
   - BLE device scanner with device list
   - Connection status and testing
   - LED control panel with color presets
   - Camera brightness monitoring
   - Real-time system status updates

**Design Principles:**

- No build step required (vanilla JS)
- Progressive enhancement
- Responsive design (mobile-friendly)
- Modern CSS with gradients and animations
- Client-side camera access using WebRTC APIs

### Communication Flow

```
User Browser (Dashboard)
    ↓ HTTP/REST
FastAPI Server (core/server.py)
    ↓ Bleak Library
Bluetooth LE Adapter
    ↓ BLE Protocol
LED Strip Device
```

### Camera Monitoring Flow

```
Browser Camera (getUserMedia)
    ↓ Canvas API
Brightness Calculation (JavaScript)
    ↓ Threshold Detection
Console Logging / Future: Backend Notification
```

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI**: Modern web framework with async support
- **Bleak**: Cross-platform Bluetooth LE library
- **Uvicorn**: ASGI server
- **OpenCV**: Camera processing (optional, CLI only)

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients, grid, flexbox
- **Vanilla JavaScript**: No framework dependencies
- **WebRTC**: Camera access via getUserMedia API

## Design Decisions

### Why Python Backend for BLE?
- Browser Web Bluetooth API has platform limitations
- Python's `bleak` provides consistent cross-platform BLE access
- Easier to debug and extend hardware communication

### Why Client-Side Camera?
- Avoids heavy OpenCV dependency in server for UI mode
- Direct browser permission flow (more secure)
- Lower latency for real-time monitoring
- No video streaming overhead

### Why No Frontend Framework?
- Keeps project simple and accessible
- No build step required
- Easy to understand and modify
- Can be migrated to React/Vue later if needed

## Future Enhancements

1. **WebSocket/SSE**: Real-time server-to-client updates
2. **Persistent Storage**: Save device pairings and preferences
3. **Authentication**: User login and session management
4. **Advanced LED Patterns**: Pre-programmed animations and effects
5. **Image Capture**: Save snapshots when brightness changes detected
6. **Frontend Framework**: Migrate to React/Vue for complex state management
7. **Database**: Store device history and monitoring logs
8. **Multi-Device Support**: Control multiple LED strips simultaneously
