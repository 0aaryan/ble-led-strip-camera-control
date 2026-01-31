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
import logging
import traceback

try:
    from bleak import BleakScanner, BleakClient
except Exception:
    BleakScanner = None
    BleakClient = None

# Configuration constants
BLE_CONNECTION_TIMEOUT = 10.0

app = FastAPI(title="LED Strip Helper API")

# Configure module logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            # Compatibility: some bleak versions provide async get_services(),
            # others expose discovered services via the `services` attribute.
            if hasattr(client, 'get_services') and callable(getattr(client, 'get_services')):
                services = await client.get_services()
            else:
                services = client.services

            svc_out = []
            for svc in services:
                try:
                    svc_uuid = getattr(svc, 'uuid', None)
                    svc_desc = getattr(svc, 'description', '')
                    chars = []
                    characteristics = getattr(svc, 'characteristics', []) or []
                    for char in characteristics:
                        try:
                            props = []
                            cprops = getattr(char, 'properties', None)
                            # properties may be None or have boolean flags
                            if cprops and getattr(cprops, 'read', False):
                                props.append('read')
                            if cprops and (getattr(cprops, 'write', False) or getattr(cprops, 'write_without_response', False)):
                                props.append('write')
                            if cprops and getattr(cprops, 'notify', False):
                                props.append('notify')
                            if cprops and getattr(cprops, 'indicate', False):
                                props.append('indicate')
                            chars.append({
                                'uuid': getattr(char, 'uuid', None),
                                'description': getattr(char, 'description', ''),
                                'properties': props,
                            })
                        except Exception:
                            logger.exception('Failed to parse characteristic for service %s', svc_uuid)
                            # Skip this characteristic and continue
                            continue
                    svc_out.append({'uuid': svc_uuid, 'description': svc_desc, 'characteristics': chars})
                except Exception:
                    logger.exception('Failed to parse service while inspecting %s', address)
                    # Skip this service and continue
                    continue
            return {'address': address, 'services': svc_out}
    except HTTPException:
        raise
    except Exception as e:
        # Log full traceback for server-side debugging
        logger.exception('Inspect failed for %s: %s', address, e)
        # Keep response message minimal but useful
        raise HTTPException(status_code=500, detail=f"inspect failed: {e}. See server logs for details.")


@app.get("/api/test-connection")
async def api_test_connection(address: str):
    """Test if LED device is connected and responsive."""
    if BleakClient is None:
        raise HTTPException(status_code=500, detail="bleak not installed on server. Install with 'pip install bleak'.")
    try:
        async with BleakClient(address, timeout=BLE_CONNECTION_TIMEOUT) as client:
            if not client.is_connected:
                return {'connected': False, 'error': 'Failed to establish connection'}
            if hasattr(client, 'get_services') and callable(getattr(client, 'get_services')):
                services = await client.get_services()
            else:
                services = client.services
            # services may be a collection or have a .services attribute depending on bleak version
            try:
                count = len(services.services) if hasattr(services, 'services') else len(services)
            except Exception:
                # Fallback: iterate to count
                count = sum(1 for _ in services)
            return {
                'connected': True,
                'address': address,
                'service_count': count,
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
