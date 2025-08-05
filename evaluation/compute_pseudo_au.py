#!/usr/bin/env python3
# compute_pseudo_au.py

import argparse
import numpy as np

"""
Compute a pseudo–AU NME (Normalized Mean Error) using MediaPipe landmarks.
口（AU12相当）と目（AU6相当）の開き具合で簡易的に表情再現度を評価します。

Usage:
    python compute_pseudo_au.py \
      --real landmarks/real.npy \
      --gen  landmarks/gen.npy
"""

def compute_pseudo_au(real_lms, gen_lms):
    errs = []
    for r, g in zip(real_lms, gen_lms):
        if r is None or g is None:
            continue
        # 口：上唇(13)–下唇(14)
        mouth_r = np.linalg.norm(r[13] - r[14])
        mouth_g = np.linalg.norm(g[13] - g[14])
        # 左目：上瞼(159)–下瞼(386)
        eye_r   = np.linalg.norm(r[159] - r[386])
        eye_g   = np.linalg.norm(g[159] - g[386])
        # 正規化に使う左右目間距離
        interocular = np.linalg.norm(r[33] - r[263])
        e_mouth = abs(mouth_r - mouth_g) / interocular
        e_eye   = abs(eye_r   -  eye_g) / interocular
        errs.append((e_mouth + e_eye) / 2)
    if not errs:
        print("Pseudo-AU: No valid frames to compute.")
    else:
        print(f"Pseudo-AU NME: {float(np.mean(errs)):.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", required=True,
                        help="Path to real landmarks .npy")
    parser.add_argument("--gen",  required=True,
                        help="Path to generated landmarks .npy")
    args = parser.parse_args()

    real = np.load(args.real, allow_pickle=True)
    gen  = np.load(args.gen,  allow_pickle=True)
    compute_pseudo_au(real, gen)

if __name__ == "__main__":
    main()
