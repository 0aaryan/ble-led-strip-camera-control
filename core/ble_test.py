"""
BLE test utilities using bleak.

Install dependency: `pip install bleak`

Usage examples:
  python core/ble_test.py scan --timeout 5
  python core/ble_test.py inspect --address AA:BB:CC:DD:EE:FF
  python core/ble_test.py write --address AA:BB:CC:DD:EE:FF --uuid 0000fff3-0000-1000-8000-00805f9b34fb --hex 0a0b0c

Notes:
- On Linux you may need BlueZ 5.43+ and appropriate permissions (run with sudo or setcap on python).
- This script lists services/characteristics and attempts to read readable ones.
"""
import asyncio
import argparse
import sys
from typing import Optional

try:
    from bleak import BleakScanner, BleakClient
except Exception as e:
    print("Missing dependency `bleak`. Install with: pip install bleak")
    raise


async def scan(timeout: float = 5.0):
    print(f"Scanning for BLE devices for {timeout} seconds...")
    devices = await BleakScanner.discover(timeout=timeout)
    if not devices:
        print("No BLE devices found.")
        return
    for i, d in enumerate(devices, 1):
        # Some bleak backends expose RSSI as an attribute, others include it in metadata.
        name = getattr(d, 'name', None) or ""
        metadata = getattr(d, 'metadata', None)
        if not name and isinstance(metadata, dict):
            name = metadata.get('local_name') or metadata.get('name') or name

        rssi = getattr(d, 'rssi', None)
        if rssi is None and isinstance(metadata, dict):
            # metadata may contain rssi under different keys depending on backend
            rssi = metadata.get('rssi') or metadata.get('RSSI') or metadata.get('rssi_dbm')

        rssi_str = f"{rssi}" if rssi is not None else "n/a"

        # Fallback: if address missing or empty, try other available attrs
        address = getattr(d, 'address', None) or (metadata.get('address') if isinstance(metadata, dict) else None) or ""

        print(f"{i}. Name: {name} | Address: {address} | RSSI: {rssi_str}")


async def inspect(address: str):
    print(f"Connecting to {address}...")
    async with BleakClient(address) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return
        print("Connected. Discovering services...")
        services = await client.get_services()
        for svc in services:
            print(f"Service {svc.uuid} | {svc.description}")
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
                props_str = ",".join(props) if props else ""
                print(f"  Char {char.uuid} | {char.description} | {props_str}")
                if 'read' in props:
                    try:
                        val = await client.read_gatt_char(char.uuid)
                        print(f"    Read ({len(val)}): {val.hex()}")
                    except Exception as e:
                        print(f"    Read failed: {e}")


async def write_example(address: str, char_uuid: str, data_hex: str, resp: bool = False):
    data = bytes.fromhex(data_hex)
    print(f"Connecting to {address} to write to {char_uuid} -> {data.hex()}")
    async with BleakClient(address) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return
        try:
            await client.write_gatt_char(char_uuid, data, response=resp)
            print("Write succeeded.")
        except Exception as e:
            print(f"Write failed: {e}")


def main(argv=None):
    parser = argparse.ArgumentParser(description='BLE test helper (requires bleak)')
    sub = parser.add_subparsers(dest='cmd')

    p_scan = sub.add_parser('scan')
    p_scan.add_argument('--timeout', type=float, default=5.0)

    p_inspect = sub.add_parser('inspect')
    p_inspect.add_argument('--address', required=True)

    p_write = sub.add_parser('write')
    p_write.add_argument('--address', required=True)
    p_write.add_argument('--uuid', required=True)
    p_write.add_argument('--hex', required=True, help='hex bytes without 0x, e.g. 0a0b0c')
    p_write.add_argument('--resp', action='store_true', help='request response if supported')

    args = parser.parse_args(argv)
    if args.cmd == 'scan':
        asyncio.run(scan(timeout=args.timeout))
    elif args.cmd == 'inspect':
        asyncio.run(inspect(args.address))
    elif args.cmd == 'write':
        asyncio.run(write_example(args.address, args.uuid, args.hex, resp=args.resp))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
