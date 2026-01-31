"""
Simple camera-based brightness detector using OpenCV.

Install dependency: `pip install opencv-python`

Usage:
  python core/camera_detect.py --device 0 --threshold 15

This captures a baseline brightness then watches for changes beyond the threshold (percent points).
"""
import argparse
import time

try:
    import cv2
    import numpy as np
except Exception:
    print("Missing dependency `opencv-python`. Install with: pip install opencv-python")
    raise


def mean_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def capture_baseline(cap, frames=30, delay=0.05):
    vals = []
    for _ in range(frames):
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Camera read failed")
        vals.append(mean_brightness(frame))
        time.sleep(delay)
    return sum(vals) / len(vals)


def monitor(device=0, threshold=15.0, save_on_change=False):
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print(f"Failed to open camera device {device}")
        return
    try:
        print("Capturing baseline...")
        baseline = capture_baseline(cap)
        print(f"Baseline brightness: {baseline:.2f}")
        print("Monitoring. Press Ctrl-C to stop.")
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Camera read failed")
                break
            val = mean_brightness(frame)
            diff = val - baseline
            if abs(diff) >= threshold:
                print(f"Change detected: brightness={val:.2f} (delta {diff:.2f})")
                if save_on_change:
                    fname = f"camera_change_{idx}.jpg"
                    cv2.imwrite(fname, frame)
                    print(f"Saved image {fname}")
                    idx += 1
                # optional: update baseline slowly to adapt
                baseline = baseline * 0.9 + val * 0.1
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        cap.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--threshold', type=float, default=15.0,
                        help='brightness delta to trigger (absolute, 0-255)')
    parser.add_argument('--save', action='store_true', help='save frames when change detected')
    args = parser.parse_args()
    monitor(device=args.device, threshold=args.threshold, save_on_change=args.save)
