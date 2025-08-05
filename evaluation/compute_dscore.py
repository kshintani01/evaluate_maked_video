#!/usr/bin/env python3
# compute_dscore.py

import glob
import pickle
import cv2
import numpy as np
import time
import os, sys

"""
Compute D-Score (Deepfake Detector Confidence) with progress and timing.
Usage:
    python compute_dscore.py
"""

current_dir   = os.path.dirname(os.path.abspath(__file__))
training_dir  = os.path.join(current_dir, '..', 'training')
sys.path.insert(0, os.path.abspath(training_dir))

def main():
    # モデルロード
    print("[D-Score] Loading detectors...")
    start_load = time.perf_counter()
    detectors = pickle.load(open("detectors.pkl", "rb"))
    load_time = time.perf_counter() - start_load
    print(f"[D-Score] Loaded {len(detectors)} detectors in {load_time:.2f}s")

    # フレーム読み込み
    frame_paths = sorted(glob.glob("frames/aligned/gen/*.png"))
    total = len(frame_paths)
    print(f"[D-Score] Processing {total} frames...")

    probs = []
    start = time.perf_counter()
    for idx, fn in enumerate(frame_paths, start=1):
        img = cv2.imread(fn)
        # 推論
        p = np.mean([det.predict(img) for det in detectors])
        probs.append(p)
        # プログレス表示
        print(f"[D-Score] Frame {idx}/{total}", end='\r', flush=True)
    elapsed = time.perf_counter() - start
    print()  # 改行

    # 平均計算
    dscore = np.mean(probs)
    print(f"[D-Score] Completed inference in {elapsed:.2f}s ({elapsed/total:.3f}s per frame)")
    print(f"[D-Score] D-Score: {dscore:.4f}")

if __name__ == '__main__':
    main()
