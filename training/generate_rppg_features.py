#!/usr/bin/env python3
"""
generate_rppg_features.py

rPPG Realness Score用のトレーニングデータ（特徴量/ラベル）を生成するスクリプト。

Usage:
    python generate_rppg_features.py \
      --real_dir path/to/real_videos \
      --gen_dir  path/to/generated_videos \
      --out_features X_train.npy \
      --out_labels   y_train.npy

出力:
    X_train.npy  : 特徴量配列 (N_samples, N_features)
    y_train.npy  : ラベル配列  (N_samples,)  1:実写／0:生成

特徴量:
  - 顔ROIを grid_size×grid_size のパッチに分割
  - 各パッチの緑チャンネル平均をフレームごとに抽出
  - Butterworth bandpass フィルタ (0.7–4Hz) を通した信号
  - パッチ間相互相関係数 (上三角) を特徴量ベクトル化

"""
import os
import argparse
import numpy as np
import cv2
from scipy.signal import butter, filtfilt


def bandpass_filter(signal, fs=30, low=0.7, high=4.0, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)


def extract_rppg_features(video_path, patch_size=64, grid_size=4, fs=30):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    if len(frames) == 0:
        raise ValueError(f"No frames in video: {video_path}")

    h, w, _ = frames[0].shape
    # パッチのステップ
    step_y = max((h - patch_size) // (grid_size - 1), 1)
    step_x = max((w - patch_size) // (grid_size - 1), 1)

    # 各パッチの時系列信号収集
    patch_signals = [[] for _ in range(grid_size * grid_size)]
    for img in frames:
        for i in range(grid_size):
            for j in range(grid_size):
                y = i * step_y
                x = j * step_x
                patch = img[y:y+patch_size, x:x+patch_size]
                # BGR -> 緑チャンネル平均
                green_mean = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB)[:, :, 1].mean()
                patch_signals[i*grid_size + j].append(green_mean)

    # バンドパスフィルタ
    filtered = []
    for sig in patch_signals:
        sig_arr = np.array(sig)
        f = bandpass_filter(sig_arr, fs=fs)
        filtered.append(f)

    # パッチ間相互相関 (上三角)
    feats = []
    P = grid_size * grid_size
    for i in range(P):
        for j in range(i+1, P):
            # 相関係数
            c = np.corrcoef(filtered[i], filtered[j])[0, 1]
            feats.append(c)
    return np.array(feats)


def main(args):
    real_files = sorted([os.path.join(args.real_dir, f) for f in os.listdir(args.real_dir)
                         if f.lower().endswith(('.mp4', '.avi', '.mov'))])
    gen_files  = sorted([os.path.join(args.gen_dir,  f) for f in os.listdir(args.gen_dir)
                         if f.lower().endswith(('.mp4', '.avi', '.mov'))])

    X, y = [], []
    print("[INFO] Extracting real video features...")
    for v in real_files:
        feats = extract_rppg_features(v, patch_size=args.patch_size,
                                      grid_size=args.grid_size, fs=args.fps)
        X.append(feats)
        y.append(1)
    print("[INFO] Extracting generated video features...")
    for v in gen_files:
        feats = extract_rppg_features(v, patch_size=args.patch_size,
                                      grid_size=args.grid_size, fs=args.fps)
        X.append(feats)
        y.append(0)

    X = np.stack(X)
    y = np.array(y)
    print(f"[INFO] Features shape: {X.shape}, Labels shape: {y.shape}")

    np.save(args.out_features, X)
    np.save(args.out_labels,   y)
    print(f"[INFO] Saved X-> {args.out_features}, y-> {args.out_labels}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--real_dir',    required=True, help='実写動画ディレクトリ')
    parser.add_argument('--gen_dir',     required=True, help='生成動画ディレクトリ')
    parser.add_argument('--out_features', required=True, help='出力X_train.npy')
    parser.add_argument('--out_labels',   required=True, help='出力y_train.npy')
    parser.add_argument('--patch_size',  type=int, default=64)
    parser.add_argument('--grid_size',   type=int, default=4)
    parser.add_argument('--fps',         type=int, default=30)
    args = parser.parse_args()
    main(args)
