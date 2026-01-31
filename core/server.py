"""
Simple FastAPI server that exposes BLE scan/inspect endpoints and serves a static single-page UI.

This backend uses `bleak` to scan and inspect BLE devices. The UI uses browser camera APIs
(getUserMedia) to access the laptop camera (so we avoid needing OpenCV in the server for the UI flow).

Run with:
  poetry install
  poetry run python -m core.server

Endpoints:
  GET /api/scan?timeout=5.0  -> JSON list of discovered devices
  GET /api/inspect?address=AA:BB:... -> JSON with services/characteristics

Static UI served at `/` (from `web/static/index.html`)
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

try:
    from bleak import BleakScanner, BleakClient
except Exception:
    BleakScanner = None
    BleakClient = None

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
    return FileResponse("web/static/index.html")


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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
