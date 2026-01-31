"""
FastAPI server that exposes BLE scan/inspect/control endpoints and serves a modern dashboard UI.

This backend uses `bleak` to scan and inspect BLE devices. The UI uses browser camera APIs
(getUserMedia) to access the laptop camera (so we avoid needing OpenCV in the server for the UI flow).

Run with:
  poetry install
  poetry run python -m core.server

Endpoints:
  GET /api/scan?timeout=5.0  -> JSON list of discovered devices
  GET /api/inspect?address=AA:BB:... -> JSON with services/characteristics
  GET /api/test-connection?address=AA:BB:... -> Test if device is connected
  POST /api/led/write -> Write data to LED characteristic

Static UI served at `/` (from `web/static/index.html`)
"""
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

try:
    from bleak import BleakScanner, BleakClient
except Exception:
    BleakScanner = None
    BleakClient = None

# Configuration constants
BLE_CONNECTION_TIMEOUT = 10.0

app = FastAPI(title="LED Strip Helper API")

# Allow local requests from the UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static UI
app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.get("/")
async def index():
    return FileResponse("web/static/dashboard.html")


@app.get("/api/scan")
async def api_scan(timeout: float = 5.0):
    if BleakScanner is None:
        raise HTTPException(status_code=500, detail="bleak not installed on server. Install with 'pip install bleak'.")
    try:
        devices = await BleakScanner.discover(timeout=timeout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"scan failed: {e}")

    out = []
    for d in devices:
        name = getattr(d, 'name', None) or ""
        metadata = getattr(d, 'metadata', None)
        if not name and isinstance(metadata, dict):
            name = metadata.get('local_name') or metadata.get('name') or name
        rssi = getattr(d, 'rssi', None)
        if rssi is None and isinstance(metadata, dict):
            rssi = metadata.get('rssi') or metadata.get('RSSI') or metadata.get('rssi_dbm')
        address = getattr(d, 'address', None) or (metadata.get('address') if isinstance(metadata, dict) else None) or ""
        out.append({
            'name': name,
            'address': address,
            'rssi': rssi,
        })
    return out


@app.get("/api/inspect")
async def api_inspect(address: str):
    if BleakClient is None:
        raise HTTPException(status_code=500, detail="bleak not installed on server. Install with 'pip install bleak'.")
    try:
        async with BleakClient(address) as client:
            if not client.is_connected:
                raise HTTPException(status_code=500, detail="failed to connect")
            services = await client.get_services()
            svc_out = []
            for svc in services:
                chars = []
                for char in svc.characteristics:
                    props = []
                    if char.properties.read:
                        props.append('read')
                    if char.properties.write or char.properties.write_without_response:
                        props.append('write')
                    if char.properties.notify:
                        props.append('notify')
                    if char.properties.indicate:
                        props.append('indicate')
                    chars.append({
                        'uuid': char.uuid,
                        'description': char.description,
                        'properties': props,
                    })
                svc_out.append({'uuid': svc.uuid, 'description': svc.description, 'characteristics': chars})
            return {'address': address, 'services': svc_out}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"inspect failed: {e}")


@app.get("/api/test-connection")
async def api_test_connection(address: str):
    """Test if LED device is connected and responsive."""
    if BleakClient is None:
        raise HTTPException(status_code=500, detail="bleak not installed on server. Install with 'pip install bleak'.")
    try:
        async with BleakClient(address, timeout=BLE_CONNECTION_TIMEOUT) as client:
            if not client.is_connected:
                return {'connected': False, 'error': 'Failed to establish connection'}
            services = await client.get_services()
            return {
                'connected': True, 
                'address': address,
                'service_count': len(services.services) if hasattr(services, 'services') else len(services)
            }
    except Exception as e:
        return {'connected': False, 'error': str(e)}


@app.post("/api/led/write")
async def api_led_write(payload: dict = Body(...)):
    """Write data to LED characteristic. Expects {address, uuid, data_hex}."""
    if BleakClient is None:
        raise HTTPException(status_code=500, detail="bleak not installed on server.")
    
    address = payload.get('address')
    char_uuid = payload.get('uuid')
    data_hex = payload.get('data_hex')
    
    if not address or not char_uuid or not data_hex:
        raise HTTPException(status_code=400, detail="Missing required fields: address, uuid, data_hex")
    
    try:
        data = bytes.fromhex(data_hex)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hex data")
    
    try:
        async with BleakClient(address, timeout=BLE_CONNECTION_TIMEOUT) as client:
            if not client.is_connected:
                raise HTTPException(status_code=500, detail="Failed to connect to device")
            await client.write_gatt_char(char_uuid, data, response=False)
            return {'success': True, 'message': f'Wrote {len(data)} bytes to {char_uuid}'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write failed: {e}")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
