#!/usr/bin/env python3
"""Phase 1: Record video. Phase 2: YOLO post-process and extract best candidates."""
import sys
import os
import time
import subprocess
import cv2
import numpy as np
from PIL import Image

BEEP_PATH = "/storage/emulated/0/Download/beep.wav"
TERMUX_MEDIA = "/data/data/com.termux/files/usr/bin/termux-media-player"
STREAM_URL = "http://192.168.2.116:8080/video"
OUTPUT_DIR = "/home/user/camera_tmp"
DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 60

def beep():
    try:
        subprocess.Popen([TERMUX_MEDIA, "play", BEEP_PATH],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def save_frame(frame, path):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    iw, ih = img.size
    if ih <= iw:
        img = img.rotate(-90, expand=True)
    img.save(path)

# --- Phase 1: Record ---
print("Waiting for stream...", flush=True)
while True:
    cap = cv2.VideoCapture(STREAM_URL)
    if cap.isOpened():
        break
    cap.release()
    time.sleep(3)

TMP_VIDEO = f"{OUTPUT_DIR}/_tmp_record.avi"

# Get stream properties
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
writer = cv2.VideoWriter(TMP_VIDEO, cv2.VideoWriter_fourcc(*'MJPG'), 10, (w, h))

beep()
print(f"Recording {DURATION}s...", flush=True)

start = time.time()
frame_idx = 0
while time.time() - start < DURATION:
    ret, frame = cap.read()
    if not ret:
        continue
    frame_idx += 1
    if frame_idx % 10 == 0:
        writer.write(frame)

cap.release()
writer.release()
beep()

total_sampled = frame_idx // 10
fsize = os.path.getsize(TMP_VIDEO) / 1024 / 1024
print(f"Recorded. {total_sampled} samples, {fsize:.1f}MB on disk.", flush=True)

# --- Phase 2: YOLO scoring ---
print("Loading YOLO...", flush=True)
from ultralytics import YOLO
model = YOLO("yolo11n.pt")

CENTER_MARGIN = 0.35
WINDOW_SEC = 5.0

# Read back from file, one frame at a time
cap2 = cv2.VideoCapture(TMP_VIDEO)
scored = []
fidx = 0
while True:
    ret, frame = cap2.read()
    if not ret:
        break
    elapsed = fidx / 10.0 * WINDOW_SEC / (WINDOW_SEC)  # approximate timing
    elapsed = fidx * 1.0  # ~1 frame per second
    fidx += 1
    h, w = frame.shape[:2]
    cx, cy = w / 2, h / 2
    results = model(frame, verbose=False, conf=0.3)

    best_score = 0
    best_label = ""
    best_conf = 0
    best_dx = 0
    best_dy = 0

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            obj_cx = (x1 + x2) / 2
            obj_cy = (y1 + y2) / 2
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls]

            dx = abs(obj_cx - cx) / w
            dy = abs(obj_cy - cy) / h

            if dx < CENTER_MARGIN and dy < CENTER_MARGIN:
                # Score: higher conf + more centered = better
                centering = 1.0 - (dx + dy)
                score = conf * centering
                if score > best_score:
                    best_score = score
                    best_label = label
                    best_conf = conf
                    best_dx = dx
                    best_dy = dy

    if best_score > 0:
        scored.append({
            "elapsed": elapsed,
            "fidx": fidx - 1,
            "score": best_score,
            "label": best_label,
            "conf": best_conf,
            "dx": best_dx,
            "dy": best_dy,
        })

cap2.release()

print(f"YOLO found {len(scored)} candidate frames.", flush=True)

# --- Pick best per time window ---
if scored:
    windows = {}
    for s in scored:
        win_id = int(s["elapsed"] // WINDOW_SEC)
        if win_id not in windows or s["score"] > windows[win_id]["score"]:
            windows[win_id] = s

    selected = sorted(windows.values(), key=lambda x: x["elapsed"])

    # Re-read only selected frames from video
    cap3 = cv2.VideoCapture(TMP_VIDEO)
    need = {s["fidx"]: s for s in selected}
    fidx = 0
    ts = time.strftime("%Y%m%d_%H%M%S")
    saved = 0
    while True:
        ret, frame = cap3.read()
        if not ret:
            break
        if fidx in need:
            saved += 1
            s = need[fidx]
            path = f"{OUTPUT_DIR}/{ts}_yolo{saved:03d}.jpg"
            save_frame(frame, path)
            print(f"[{saved}] t={s['elapsed']:.1f}s {s['label']}({s['conf']:.2f}) "
                  f"score={s['score']:.2f} offset=({s['dx']:.2f},{s['dy']:.2f})")
        fidx += 1
    cap3.release()

    print(f"DONE: {saved} best frames saved from {len(scored)} candidates.")
else:
    print("DONE: No objects detected near center.")

# Cleanup temp video
if os.path.exists(TMP_VIDEO):
    os.remove(TMP_VIDEO)
    print("Temp video cleaned up.")
