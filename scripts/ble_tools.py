#!/usr/bin/env python3
"""
Lightweight BLE tools for scanning, inspecting and writing to characteristics.

Usage:
  python scripts/ble_tools.py scan --timeout 5
  python scripts/ble_tools.py inspect --address AC:C2:01:39:3D:5D --read
  python scripts/ble_tools.py write --address AC:C2:01:39:3D:5D --uuid 0000ffe1-0000-1000-8000-00805f9b34fb --hex 0a0b0c

The script is defensive about bleak versions: it uses `await client.get_services()` if
available, otherwise falls back to `client.services`.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Optional

try:
    from bleak import BleakScanner, BleakClient
except Exception:
    print("Missing dependency `bleak`. Install with: pip install bleak")
    raise


async def scan(timeout: float = 5.0) -> None:
    print(f"Scanning for BLE devices for {timeout} seconds...")
    devices = await BleakScanner.discover(timeout=timeout)
    if not devices:
        print("No BLE devices found.")
        return
    for i, d in enumerate(devices, 1):
        name = getattr(d, 'name', None) or ""
        metadata = getattr(d, 'metadata', None)
        if not name and isinstance(metadata, dict):
            name = metadata.get('local_name') or metadata.get('name') or name
        rssi = getattr(d, 'rssi', None)
        if rssi is None and isinstance(metadata, dict):
            rssi = metadata.get('rssi') or metadata.get('RSSI') or metadata.get('rssi_dbm')
        address = getattr(d, 'address', None) or (metadata.get('address') if isinstance(metadata, dict) else None) or ""
        print(f"{i}. Name: {name} | Address: {address} | RSSI: {rssi if rssi is not None else 'n/a'}")


async def _get_services_from_client(client: BleakClient):
    # Return services in a uniform way regardless of bleak version
    if hasattr(client, 'get_services') and callable(getattr(client, 'get_services')):
        # In older bleak, get_services was async; in newer, services is a property
        return await client.get_services()
    return client.services


async def inspect(address: str, read: bool = False) -> None:
    print(f"Connecting to {address}...")
    try:
        async with BleakClient(address) as client:
            if not client.is_connected:
                print("Failed to connect.")
                return
            print("Connected. Discovering services...")
            # call or attribute
            services = await _get_services_from_client(client)

            for svc in services:
                svc_uuid = getattr(svc, 'uuid', None)
                svc_desc = getattr(svc, 'description', '')
                print(f"\nService: {svc_uuid}\n{svc_desc}\n")
                characteristics = getattr(svc, 'characteristics', []) or []
                for char in characteristics:
                    c_uuid = getattr(char, 'uuid', None)
                    c_desc = getattr(char, 'description', '')
                    cprops = getattr(char, 'properties', None)
                    props = []
                    if cprops:
                        # properties might be a list of strings or an object with boolean attributes
                        if isinstance(cprops, (list, tuple)):
                            props = list(cprops)
                        else:
                            if getattr(cprops, 'read', False):
                                props.append('read')
                            if getattr(cprops, 'write', False):
                                props.append('write')
                            if getattr(cprops, 'write_without_response', False):
                                props.append('write-without-response')
                            if getattr(cprops, 'notify', False):
                                props.append('notify')
                            if getattr(cprops, 'indicate', False):
                                props.append('indicate')
                    print(f"  UUID: {c_uuid}\n    {c_desc} • Properties: {','.join(props) if props else 'none'}")
                    if read and 'read' in props:
                        try:
                            val = await client.read_gatt_char(c_uuid)
                            print(f"    Read ({len(val)}): {val.hex()}")
                        except Exception as e:
                            print(f"    Read failed: {e}")
    except Exception as e:
        print(f"Inspect failed: {e}")


async def write(address: str, char_uuid: Optional[str], data_hex: str, response: bool = False) -> None:
    data = bytes.fromhex(data_hex)
    print(f"Connecting to {address} to write -> {data.hex()}")
    try:
        async with BleakClient(address) as client:
            if not client.is_connected:
                print("Failed to connect.")
                return
            services = await _get_services_from_client(client)

            # Flatten characteristics
            chars = []
            for svc in services:
                for char in getattr(svc, 'characteristics', []) or []:
                    chars.append(char)

            # If UUID not provided, pick first writable char
            target = None
            if char_uuid:
                for c in chars:
                    if getattr(c, 'uuid', None) and c.uuid.lower() == char_uuid.lower():
                        target = c
                        break
                if not target:
                    print(f"Characteristic {char_uuid} was not found!")
                    print("Available characteristics:")
                    for c in chars:
                        print(f"  {getattr(c,'uuid',None)} - {getattr(c,'description','')} - props={getattr(c,'properties',None)}")
                    return
            else:
                for c in chars:
                    p = getattr(c, 'properties', None)
                    if p and (getattr(p, 'write', False) or getattr(p, 'write_without_response', False)):
                        target = c
                        break
                if not target:
                    print("No writable characteristic found. Available characteristics:")
                    for c in chars:
                        print(f"  {getattr(c,'uuid',None)} - {getattr(c,'description','')} - props={getattr(c,'properties',None)}")
                    return

            try:
                await client.write_gatt_char(getattr(target, 'uuid'), data, response=response)
                print("Write succeeded.")
            except Exception as e:
                print(f"Write failed: {e}")

    except Exception as e:
        print(f"Connection/Write failed: {e}")


def main(argv=None):
    parser = argparse.ArgumentParser(description='BLE helper (requires bleak)')
    sub = parser.add_subparsers(dest='cmd')

    p_scan = sub.add_parser('scan')
    p_scan.add_argument('--timeout', type=float, default=5.0)

    p_inspect = sub.add_parser('inspect')
    p_inspect.add_argument('--address', required=True)
    p_inspect.add_argument('--read', action='store_true', help='attempt read on readable characteristics')

    p_write = sub.add_parser('write')
    p_write.add_argument('--address', required=True)
    p_write.add_argument('--uuid', required=False, help='characteristic UUID to write; if omitted, picks first writable')
    p_write.add_argument('--hex', required=True, help='hex bytes without 0x, e.g. 0a0b0c')
    p_write.add_argument('--resp', action='store_true', help='request response if supported')

    args = parser.parse_args(argv)
    if args.cmd == 'scan':
        asyncio.run(scan(timeout=args.timeout))
    elif args.cmd == 'inspect':
        asyncio.run(inspect(args.address, read=args.read))
    elif args.cmd == 'write':
        asyncio.run(write(args.address, args.uuid, args.hex, response=args.resp))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
