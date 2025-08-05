#!/usr/bin/env python3
# compute_dtw.py

import argparse
import numpy as np
from dtw import dtw

"""
Compute DTW-normalized distance between two time series feature arrays.
Usage:
    python compute_dtw.py --real features/real.npy --gen features/gen.npy
"""

def load_features(path):
    return np.load(path)


def main():
    parser = argparse.ArgumentParser(description="Compute DTW-normalized distance")
    parser.add_argument("--real", default="features/real.npy",
                        help="Path to real feature .npy file")
    parser.add_argument("--gen",  default="features/gen.npy",
                        help="Path to generated feature .npy file")
    args = parser.parse_args()

    real_seq = load_features(args.real)
    gen_seq  = load_features(args.gen)

    # Use dtw-python's dist_method parameter
    res = dtw(real_seq, gen_seq,
              dist_method=lambda x, y: np.linalg.norm(x - y),
              keep_internals=True)

    dtw_norm = res.distance / len(res.index1)
    print(f"DTW-norm: {dtw_norm:.3f}")

if __name__ == '__main__':
    main()
