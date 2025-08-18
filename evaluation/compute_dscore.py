#!/usr/bin/env python3
# compute_dscore_compare_simple.py
# real と gen の両方を処理して比較し、ターミナルに結果表示

import argparse
import glob
import pickle
import cv2
import numpy as np
import os, sys, time
from statistics import median

current_dir   = os.path.dirname(os.path.abspath(__file__))
training_dir  = os.path.join(current_dir, '..', 'training')
sys.path.insert(0, os.path.abspath(training_dir))

def load_detectors(pkl_path: str):
    t0 = time.perf_counter()
    detectors = pickle.load(open(pkl_path, "rb"))
    print(f"[D-Score] Loaded {len(detectors)} detectors in {time.perf_counter()-t0:.2f}s")
    return detectors

def list_frames(dir: str):
    paths = sorted(glob.glob(dir))
    print(f"[Frames] {dir} -> {len(paths)} frames")
    return paths

def infer_prob_real(detectors, frame_paths):
    """各フレームについて、全検出器の P(real) を平均して返す（1D配列）"""
    probs = []
    t0 = time.perf_counter()
    total = len(frame_paths)
    for i, fn in enumerate(frame_paths, 1):
        img = cv2.imread(fn)  # BGR
        p = np.mean([det.predict(img) for det in detectors])  # 各detectorのP(real)を平均
        probs.append(p)
        if i % 50 == 0 or i == total:
            dt = time.perf_counter() - t0
            print(f"[Infer] {i}/{total} frames  avg {dt/max(1,i):.3f}s/frame", end='\r', flush=True)
    print()
    return np.asarray(probs, dtype=np.float32)

def summarize(name, arr):
    arr = np.asarray(arr, dtype=np.float32)
    summary = {
        "n": len(arr),
        "mean": float(np.mean(arr)) if len(arr) else float('nan'),
        "std":  float(np.std(arr, ddof=1)) if len(arr) > 1 else float('nan'),
        "p25":  float(np.percentile(arr, 25)) if len(arr) else float('nan'),
        "p50":  float(median(arr)) if len(arr) else float('nan'),
        "p75":  float(np.percentile(arr, 75)) if len(arr) else float('nan'),
        "min":  float(np.min(arr)) if len(arr) else float('nan'),
        "max":  float(np.max(arr)) if len(arr) else float('nan'),
    }
    print(f"\n[{name}] n={summary['n']}  mean={summary['mean']:.4f}  std={summary['std']:.4f}  "
          f"p25={summary['p25']:.4f}  p50={summary['p50']:.4f}  p75={summary['p75']:.4f}  "
          f"min={summary['min']:.4f}  max={summary['max']:.4f}")
    return summary

def cohens_d(x, y):
    x = np.asarray(x); y = np.asarray(y)
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2: return float('nan')
    sx2 = np.var(x, ddof=1); sy2 = np.var(y, ddof=1)
    sp = np.sqrt(((nx-1)*sx2 + (ny-1)*sy2) / (nx+ny-2))
    if sp == 0: return 0.0
    return (np.mean(x) - np.mean(y)) / sp

def main():
    ap = argparse.ArgumentParser(description="Compute D-Score for real and gen, compare in terminal")
    ap.add_argument("--detectors", default="detectors.pkl", help="Path to detectors.pkl")
    ap.add_argument("--real", default="frames/aligned/real/*.png", help="Glob for real frames")
    ap.add_argument("--gen",  default="frames/aligned/gen/*.png",  help="Glob for gen frames")
    args = ap.parse_args()

    detectors = load_detectors(args.detectors)

    real_paths = list_frames(args.real)
    gen_paths  = list_frames(args.gen)

    if len(real_paths) == 0 and len(gen_paths) == 0:
        print("[Error] No frames found for both real and gen. Check paths.")
        return

    p_real_real = infer_prob_real(detectors, real_paths) if len(real_paths) else np.array([])
    p_real_gen  = infer_prob_real(detectors, gen_paths)  if len(gen_paths)  else np.array([])

    s_real = summarize("REAL  (P(real))", p_real_real) if len(p_real_real) else None
    s_gen  = summarize("GEN   (P(real))", p_real_gen)  if len(p_real_gen)  else None

    if s_real and s_gen:
        gap = s_real["mean"] - s_gen["mean"]
        d   = cohens_d(p_real_real, p_real_gen)
        print(f"\n[Compare] Gap (mean_real - mean_gen) = {gap:.4f}")
        print(f"[Compare] Cohen's d (effect size)     = {d:.3f}")
        if s_real["mean"] < s_gen["mean"]:
            print("[Warn] mean_real < mean_gen  → 向きが逆の可能性。predict が P(fake) を返していないか確認してください。")

if __name__ == "__main__":
    main()