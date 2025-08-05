#!/usr/bin/env python3
# estimate_offset.py

import argparse
import numpy as np
from scipy.signal import correlate
from extract_sequence_features import compute_sequence  # 先ほどのスクリプト

def estimate_offset(real_seq, gen_seq):
    # ここでは mouth+eye 2次元を合成した1次元信号で推定
    sig_r = real_seq.mean(axis=1)  
    sig_g = gen_seq.mean(axis=1)
    corr = correlate(sig_r - sig_r.mean(), sig_g - sig_g.mean(), mode='full')
    lag = corr.argmax() - (len(sig_r) - 1)
    return lag

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--aligned_real", required=True)
    p.add_argument("--aligned_gen",  required=True)
    p.add_argument("--grid", type=int, default=4)
    p.add_argument("--patch", type=int, default=64)
    args = p.parse_args()

    # 時系列特徴を抽出
    real_seq = compute_sequence(args.aligned_real)
    gen_seq  = compute_sequence(args.aligned_gen)

    lag = estimate_offset(real_seq, gen_seq)
    print(f"Estimated frame offset (real → gen): {lag}")

if __name__=="__main__":
    main()
