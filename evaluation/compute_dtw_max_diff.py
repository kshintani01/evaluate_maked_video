#!/usr/bin/env python3
# compute_dtw_max_diff.py

import argparse
import numpy as np
from dtw import dtw

"""
Compute DTW-normalized distance across frame shifts, and report the maximum.
Shifts the generated sequence relative to the real sequence, computes DTW-norm for each shift,
and outputs the shift with the highest normalized distance.

Usage:
    python compute_dtw_max_diff.py \
        --real features/real.npy \
        --gen  features/gen.npy \
        --min_shift -10 \
        --max_shift 10
"""

def load_features(path):
    return np.load(path)


def compute_dtw_norm(seq1, seq2):
    # Use dtw-python's dist_method parameter
    res = dtw(seq1, seq2,
              dist_method=lambda x, y: np.linalg.norm(x - y),
              keep_internals=True)
    return res.distance / len(res.index1)


def main():
    parser = argparse.ArgumentParser(description="Compute max DTW-norm over shifts")
    parser.add_argument("--real", required=True,
                        help="Path to real feature .npy file")
    parser.add_argument("--gen",  required=True,
                        help="Path to generated feature .npy file")
    parser.add_argument("--min_shift", type=int, default=-10,
                        help="Minimum frame shift to try (negative means gen leads)")
    parser.add_argument("--max_shift", type=int, default=10,
                        help="Maximum frame shift to try (positive means real leads)")
    args = parser.parse_args()

    real_seq = load_features(args.real)
    gen_seq  = load_features(args.gen)

    best_norm = -np.inf
    best_shift = None

    print(f"Evaluating shifts from {args.min_shift} to {args.max_shift}...")
    for shift in range(args.min_shift, args.max_shift + 1):
        if shift > 0:
            s1 = real_seq[shift:]
            s2 = gen_seq[:len(s1)]
        elif shift < 0:
            s2 = gen_seq[-shift:]
            s1 = real_seq[:len(s2)]
        else:
            s1, s2 = real_seq, gen_seq
        if len(s1) < 2 or len(s2) < 2:
            continue
        norm = compute_dtw_norm(s1, s2)
        print(f" Shift {shift:3d}: DTW-norm = {norm:.3f}")
        if norm > best_norm:
            best_norm = norm
            best_shift = shift

    if best_shift is None:
        print("No valid shifts evaluated.")
    else:
        print(f"\nMax DTW-norm {best_norm:.3f} at shift {best_shift}")

if __name__ == '__main__':
    main()
