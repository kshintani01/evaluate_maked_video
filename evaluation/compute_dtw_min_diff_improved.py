#!/usr/bin/env python3
# compute_dtw_min_diff_improved.py

import argparse
import numpy as np
from dtw import dtw

"""
Improved DTW evaluation with better handling of invalid frames.
"""

def load_features(path):
    return np.load(path)

def remove_invalid_frames(seq, threshold=1e-6):
    """Remove frames where both mouth and eye features are near zero (invalid detection)"""
    valid_mask = np.sum(np.abs(seq), axis=1) > threshold
    return seq[valid_mask], valid_mask

def compute_dtw_norm(seq1, seq2):
    """Compute DTW-normalized distance"""
    res = dtw(seq1, seq2,
              dist_method=lambda x, y: np.linalg.norm(x - y),
              keep_internals=True)
    return res.distance / len(res.index1)

def main():
    parser = argparse.ArgumentParser(description="Improved DTW evaluation")
    parser.add_argument("--real", required=True)
    parser.add_argument("--gen",  required=True)
    parser.add_argument("--min_shift", type=int, default=-30)
    parser.add_argument("--max_shift", type=int, default=30)
    parser.add_argument("--remove_invalid", action="store_true", 
                       help="Remove frames with invalid face detection")
    args = parser.parse_args()

    real_seq = load_features(args.real)
    gen_seq  = load_features(args.gen)
    
    print(f"Original shapes: Real={real_seq.shape}, Gen={gen_seq.shape}")
    
    if args.remove_invalid:
        real_seq_clean, real_mask = remove_invalid_frames(real_seq)
        gen_seq_clean, gen_mask = remove_invalid_frames(gen_seq)
        print(f"After removing invalid: Real={real_seq_clean.shape}, Gen={gen_seq_clean.shape}")
        real_seq, gen_seq = real_seq_clean, gen_seq_clean

    best_norm = np.inf
    best_shift = None
    results = []

    print(f"\nEvaluating shifts from {args.min_shift} to {args.max_shift}...")
    for shift in range(args.min_shift, args.max_shift + 1):
        # Align sequences based on shift
        if shift > 0:
            s1 = real_seq[shift:]
            s2 = gen_seq[:len(s1)]
        elif shift < 0:
            s2 = gen_seq[-shift:]
            s1 = real_seq[:len(s2)]
        else:
            s1, s2 = real_seq, gen_seq
            
        if len(s1) < 10:  # Minimum sequence length
            continue
            
        norm = compute_dtw_norm(s1, s2)
        results.append((shift, norm))
        print(f" Shift {shift:3d}: DTW-norm = {norm:.3f} (lengths: {len(s1)}, {len(s2)})")
        
        if norm < best_norm:
            best_norm = norm
            best_shift = shift

    if best_shift is None:
        print("No valid shifts evaluated.")
    else:
        print(f"\nMin DTW-norm {best_norm:.3f} at shift {best_shift}")
        
        # Additional analysis
        if best_shift > 0:
            print(f"→ Real video leads by {best_shift} frames")
        elif best_shift < 0:
            print(f"→ Generated video leads by {-best_shift} frames")
        else:
            print("→ Videos are synchronized")

if __name__ == '__main__':
    main()