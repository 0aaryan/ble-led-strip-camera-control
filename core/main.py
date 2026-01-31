"""
CLI wrapper to run BLE and camera test helpers.

Usage examples:
  python core/main.py ble scan --timeout 5
  python core/main.py ble inspect --address AA:BB:CC:DD:EE:FF
  python core/main.py camera --device 0 --threshold 15

Make sure to install dependencies:
  pip install bleak opencv-python
"""
import argparse
import sys


def main(argv=None):
	parser = argparse.ArgumentParser(description='LED strip test utilities')
	sub = parser.add_subparsers(dest='tool')

	p_ble = sub.add_parser('ble', help='BLE helpers (scan/inspect/write)')
	# Accept arbitrary sub-args for ble helper and forward them
	p_ble.add_argument('ble_cmd', nargs=argparse.REMAINDER,
					   help='Arguments forwarded to core.ble_test')

	p_cam = sub.add_parser('camera', help='Camera brightness monitor')
	p_cam.add_argument('--device', type=int, default=0)
	p_cam.add_argument('--threshold', type=float, default=15.0,
					   help='brightness delta to trigger (absolute, 0-255)')
	p_cam.add_argument('--save', action='store_true', help='save frames when change detected')

	args = parser.parse_args(argv)
	if args.tool == 'ble':
		# Lazy import to avoid requiring bleak unless needed
		try:
			from core import ble_test
		except Exception as e:
			print('Failed to import BLE helper. Ensure `bleak` is installed: pip install bleak')
			raise
		# Forward the remaining args to ble_test.main
		# If nothing provided, show help
		if not args.ble_cmd:
			print('Usage: python core/main.py ble <scan|inspect|write> [--options]')
			return
		# ble_test.main expects normal argv list
		# args.ble_cmd is a list starting with the subcommand
		ble_test.main(args.ble_cmd)
	elif args.tool == 'camera':
		try:
			from core import camera_detect
		except Exception as e:
			print('Failed to import camera helper. Ensure `opencv-python` is installed: pip install opencv-python')
			raise
		camera_detect.monitor(device=args.device, threshold=args.threshold, save_on_change=args.save)
	else:
		parser.print_help()


if __name__ == '__main__':
	main()
