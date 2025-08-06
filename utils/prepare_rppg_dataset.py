#!/usr/bin/env python3
import argparse
import numpy as np

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', required=True,
                   help='features ディレクトリのパス')
    p.add_argument('--output-features', required=True,
                   help='出力する特徴量ファイルパス')
    p.add_argument('--output-labels', required=True,
                   help='出力するラベルファイルパス')
    args = p.parse_args()

    real = np.load(f"{args.input_dir}/real.npy")
    gen  = np.load(f"{args.input_dir}/gen.npy")
    X = np.vstack([real, gen])
    y = np.hstack([np.zeros(len(real)), np.ones(len(gen))])

    np.save(args.output_features, X)
    np.save(args.output_labels, y)
    print(f"Saved {args.output_features} {X.shape}, {args.output_labels} {y.shape}")

if __name__ == '__main__':
    main()