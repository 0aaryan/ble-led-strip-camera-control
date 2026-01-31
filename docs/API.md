# API Documentation

## Base URL
```
http://127.0.0.1:8000/api
```

**Note:** This is the default local development URL. In production, replace with your actual server address and port.

## Endpoints

### GET /api/scan
Scan for nearby BLE devices.

**Query Parameters:**
- `timeout` (float, optional): Scan timeout in seconds. Default: 5.0

**Response:**
```json
[
  {
    "name": "LED Strip",
    "address": "AA:BB:CC:DD:EE:FF",
    "rssi": -65
  }
]
```

### GET /api/inspect
Inspect services and characteristics of a BLE device.

**Query Parameters:**
- `address` (string, required): BLE device address

**Response:**
```json
{
  "address": "AA:BB:CC:DD:EE:FF",
  "services": [
    {
      "uuid": "0000fff0-0000-1000-8000-00805f9b34fb",
      "description": "Vendor specific",
      "characteristics": [
        {
          "uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
          "description": "Vendor specific",
          "properties": ["write", "read"]
        }
      ]
    }
  ]
}
```

### GET /api/test-connection
Test if a BLE device is connected and responsive.

**Query Parameters:**
- `address` (string, required): BLE device address

**Response (Success):**
```json
{
  "connected": true,
  "address": "AA:BB:CC:DD:EE:FF",
  "service_count": 3
}
```

**Response (Failure):**
```json
{
  "connected": false,
  "error": "Connection timeout"
}
```

### POST /api/led/write
Write data to an LED characteristic.

**Request Body:**
```json
{
  "address": "AA:BB:CC:DD:EE:FF",
  "uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
  "data_hex": "ff0000"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Wrote 3 bytes to 0000fff3-0000-1000-8000-00805f9b34fb"
}
```

**Response (Error):**
```json
{
  "detail": "Write failed: [error message]"
}
```

## Common LED Commands

### Color Control
Most LED strips use a 3-byte RGB format:

- Red: `ff0000`
- Green: `00ff00`
- Blue: `0000ff`
- White: `ffffff`
- Off: `000000`
- Yellow: `ffff00`
- Cyan: `00ffff`
- Magenta: `ff00ff`

### Example Usage

**Turn LED Red:**
```bash
curl -X POST http://127.0.0.1:8000/api/led/write \
  -H "Content-Type: application/json" \
  -d '{
    "address": "AA:BB:CC:DD:EE:FF",
    "uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
    "data_hex": "ff0000"
  }'
```

**Scan for Devices:**
```bash
curl http://127.0.0.1:8000/api/scan?timeout=5
```

**Test Connection:**
```bash
curl "http://127.0.0.1:8000/api/test-connection?address=AA:BB:CC:DD:EE:FF"
```
