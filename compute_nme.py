#!/usr/bin/env python3
# compute_nme.py

import argparse
import numpy as np

"""
Compute Normalized Mean Error (NME) between two sets of landmarks.
Usage:
    python compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy
"""

def compute_nme(real_lms, gen_lms):
    errs = []
    for r, g in zip(real_lms, gen_lms):
        if r is None or g is None:
            continue
        # Inter-ocular distance (left eye outer [33], right eye outer [263])
        d = np.linalg.norm(r[33] - r[263])
        errs.append(np.linalg.norm(r - g, axis=1).mean() / d)
    if not errs:
        print("NME: No valid frames to compute.")
    else:
        print(f"NME: {float(np.mean(errs)):.4f}")


def main():
    parser = argparse.ArgumentParser(description="Compute NME from landmark .npy files")
    parser.add_argument("--real", required=True, help="Path to real landmarks .npy file")
    parser.add_argument("--gen",  required=True, help="Path to generated landmarks .npy file")
    args = parser.parse_args()

    # Load landmark arrays (dtype=object, list of (K,2) or None)
    real_lms = np.load(args.real, allow_pickle=True)
    gen_lms  = np.load(args.gen,  allow_pickle=True)

    compute_nme(real_lms, gen_lms)

if __name__ == '__main__':
    main()
