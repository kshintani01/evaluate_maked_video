#!/usr/bin/env python3
"""
generate_rppg_model.py

rPPG Realness Score用ロジスティック回帰モデルを学習・保存するスクリプト。
事前に特徴量ファイルとラベルファイルが必要です。

- 特徴量データ: X_train.npy (shape=(N_samples, N_features))
- ラベルデータ:   y_train.npy (shape=(N_samples,)), 1:実写、0:生成

Usage:
    python generate_rppg_model.py --features X_train.npy --labels y_train.npy
"""

import argparse
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def main(args):
    # 特徴量とラベルの読み込み
    X = np.load(args.features)
    y = np.load(args.labels)

    # 学習 / 検証データ分割
    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # モデル定義
    model = LogisticRegression(max_iter=1000)
    # 学習
    model.fit(X_tr, y_tr)

    # 検証精度確認
    y_pred = model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    print(f"Validation Accuracy: {acc*100:.2f}%")

    # モデル保存
    with open('rppg_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("rppg_model.pkl を作成しました。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--features', required=True, help='特徴量.npyファイルパス')
    parser.add_argument('--labels', required=True, help='ラベル.npyファイルパス')
    args = parser.parse_args()
    main(args)
