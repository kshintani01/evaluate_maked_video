#!/usr/bin/env python3
# compute_rppg.py

import argparse
import glob
import pickle
import numpy as np
import cv2
from scipy.signal import butter, filtfilt

"""
Compute rPPG Realness Score using a trained logistic regression model.
Extracts patch-based green-channel signals from aligned frames,
filters them, computes pairwise correlations, and predicts realness.
Usage:
    python compute_rppg.py --aligned_dir frames/aligned/gen --model rppg_model.pkl
"""


def bandpass(signal, fs=30, low=0.7, high=4.0, order=4):
    """
    Apply Butterworth bandpass filter to a 1D signal.
    """
    nyq = 0.5 * fs
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)


def extract_rppg_features(aligned_dir, grid_size=4, patch_size=64, fs=30):
    """
    From aligned frame images, extract rPPG features:
      - Split each frame into grid_size x grid_size patches
      - Compute green-channel mean for each patch across frames
      - Bandpass filter each patch signal
      - Compute pairwise correlations between patch signals
    Returns feature vector (length P*(P-1)/2).
    """
    # Collect all PNG filenames
    files = sorted(glob.glob(f"{aligned_dir}/*.png"))
    if not files:
        raise FileNotFoundError(f"No aligned frames found in {aligned_dir}")
    # Determine patch grid steps
    img0 = cv2.imread(files[0])
    h, w = img0.shape[:2]
    step_y = max((h - patch_size) // (grid_size - 1), 1)
    step_x = max((w - patch_size) // (grid_size - 1), 1)
    P = grid_size * grid_size
    # Initialize list for each patch signal
    signals = [[] for _ in range(P)]
    # Extract green-channel mean per patch per frame
    for fn in files:
        img = cv2.imread(fn)
        for i in range(grid_size):
            for j in range(grid_size):
                y = i * step_y
                x = j * step_x
                patch = img[y:y+patch_size, x:x+patch_size]
                signals[i*grid_size + j].append(patch[:, :, 1].mean())
    # Convert to array and filter
    signals = np.array(signals)  # shape (P, N_frames)
    filtered = np.array([bandpass(sig, fs=fs, low=0.7, high=4.0) for sig in signals])
    # Compute pairwise correlation features
    feats = []
    for i in range(P):
        for j in range(i+1, P):
            c = np.corrcoef(filtered[i], filtered[j])[0, 1]
            feats.append(c)
    return np.array(feats)


def main():
    parser = argparse.ArgumentParser(description="Compute rPPG Realness Score")
    parser.add_argument("--aligned_dir", default="frames/aligned/gen",
                        help="Directory of aligned frames to process")
    parser.add_argument("--model", default="rppg_model.pkl",
                        help="Path to trained logistic regression model")
    args = parser.parse_args()

    # Extract features
    feats = extract_rppg_features(args.aligned_dir)
    # Load trained logistic regression model
    with open(args.model, 'rb') as f:
        model = pickle.load(f)
    # Predict probability of being real (class 1)
    proba = model.predict_proba(feats.reshape(1, -1))[0]
    p_real = proba[1]
    print(f"rPPG Realness Score: {p_real:.3f}")

if __name__ == '__main__':
    main()
