# Real Communication 動画評価パイプライン

本プロジェクトは、実写動画と生成動画を比較し、6つの評価指標を一貫して算出するパイプラインです。各ステップをスクリプト化し、独立して実行・テストできる構成になっています。

---

## 📋 ディレクトリ構成

```
generated_movie/
├─ preprocessing/           # 前処理関連スクリプト
│   ├─ shift_videos_trim.py     # 動画をフレーム単位でトリミング（シフト）
│   ├─ preprocess.py            # リサンプリング・フレーム抽出・空間アライン
│   ├─ extract_landmarks.py     # 顔ランドマーク抽出
│   └─ extract_sequence_features.py # 口/目開度時系列抽出
│   └─ clip_split.py            # クリップファイル生成（FVD用）
│
├─ training/                # モデル準備・学習スクリプト
│   ├─ detectors.py             # Deepfake 検出器定義
│   ├─ generate_detectors.py    # detectors.pkl 生成
│   ├─ generate_rppg_features.py# rPPG 特徴量/ラベル生成
│   └─ generate_rppg_model.py   # rPPG ロジスティック回帰学習
│
├─ evaluation/              # 評価指標計算スクリプト
│   ├─ compute_fvd.py           # FVD（Fréchet Video Distance）
│   ├─ compute_nme.py           # NME（Normalized Mean Error）
│   ├─ compute_dscore.py        # D-Score（Deepfake 判定確率）
│   ├─ compute_dtw.py           # DTW-norm
│   ├─ compute_dtw_max_diff.py  # DTW-norm 最大シフト探索
│   ├─ compute_rppg.py          # rPPG Realness Score
│   ├─ compute_pseudo_au.py     # Pseudo-AU NME
│   └─ compute_au_mae.py        # OpenFace AU MAE（オプション）
│
├─ utils/                   # 共通ユーティリティ
│   └─ estimate_offset.py       # 時系列相互相関オフセット推定
│
├─ requirements.txt         # Python 依存ライブラリ一覧
└─ README.md                # 本ドキュメント
```

---

## 🛠️ 必要環境・インストール

```bash
# Python3.8 以降推奨
git clone <リポジトリURL>
cd generated_movie
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**追加依存**

- FFmpeg / FFprobe（`preprocessing`）
- MediaPipe（顔ランドマーク検出）

---

## 🚀 実行手順（例）

### 1. 動画シフト（preprocessing）

```bash
python preprocessing/shift_videos_trim.py \
  --real real_0804.mp4 \
  --gen  Receiver_0804.mp4 \
  --shift 16 --fps 30 \
  --out_real  real_shifted.mp4 \
  --out_gen   Receiver_shifted.mp4
```

### 2. 前処理（preprocessing）

```bash
python preprocessing/preprocess.py \
  --real real_shifted.mp4 \
  --gen  Receiver_shifted.mp4
```

### 3. ランドマーク抽出（preprocessing）

```bash
python preprocessing/extract_landmarks.py \
  --aligned_dir frames/aligned/real \
  --out_npy    landmarks/real.npy
python preprocessing/extract_landmarks.py \
  --aligned_dir frames/aligned/gen  \
  --out_npy    landmarks/gen.npy
```

### 4. シーケンス特徴抽出（preprocessing）

```bash
python preprocessing/extract_sequence_features.py \
  --aligned_real frames/aligned/real \
  --aligned_gen  frames/aligned/gen  \
  --out_dir      features
```

### 5. モデル準備・学習（training）

```bash
python training/generate_detectors.py   # detectors.pkl を生成
python training/generate_rppg_features.py \
  --real_dir real_videos --gen_dir gen_videos \
  --out_features X_train.npy --out_labels y_train.npy
python training/generate_rppg_model.py \
  --features X_train.npy --labels y_train.npy
```

### 6. 評価指標計算（evaluation）

```bash
python evaluation/compute_fvd.py
python evaluation/compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy
python evaluation/compute_dscore.py
python evaluation/compute_dtw_max_diff.py --real features/real.npy --gen features/gen.npy --min_shift -20 --max_shift 20
python evaluation/compute_rppg.py --aligned_dir frames/aligned/gen --model rppg_model.pkl
python evaluation/compute_pseudo_au.py --real landmarks/real.npy --gen landmarks/gen.npy
# (オプション) OpenFace AU MAE:
python evaluation/compute_au_mae.py
```

各スクリプトが実行結果をターミナルに出力します。

---

## 📈 開発メモ

- **精度改善**: 検出モデルのファインチューニングやシーケンス特徴の追加。
- **パラメータ調整**: リサンプル解像度／fps、rPPGのパッチ設定など。
- **拡張案**: GUI化、自動レポート生成、本来の AU MAE 復活。

---

