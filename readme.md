# Real Communication 動画評価パイプライン

本プロジェクトは、実写動画と生成動画を比較し、6つの評価指標を一貫して算出するパイプラインです。各ステップをスクリプト化し、独立して実行・テストできる構成になっています。

---

## 📁 ディレクトリ構成

```plain
generated_movie/
├─ preprocessing/           # 前処理関連
│   ├─ shift_videos_trim.py       # 動画シフト（フレームトリミング）
│   ├─ preprocess.py              # リサンプリング・フレーム抽出・アライン
│   ├─ extract_landmarks.py       # 顔ランドマーク抽出
│   ├─ extract_sequence_features.py # 口/目開度時系列抽出
│   └─ clip_split.py              # クリップ生成（FVD用）
│
├─ training/                # モデル準備・学習
│   ├─ detectors.py               # Deepfake検出器定義
│   ├─ generate_detectors.py      # detectors.pkl生成
│   └─ generate_rppg_model.py     # rPPGモデル学習
│
├─ evaluation/              # 指標計算
│   ├─ compute_fvd.py             # FVD
│   ├─ compute_nme.py             # NME
│   ├─ compute_dscore.py          # D-Score
│   ├─ compute_dtw.py             # DTW-norm
│   ├─ compute_dtw_max_diff.py    # DTWシフト最適化
│   ├─ compute_rppg.py            # rPPGスコア
│   ├─ compute_pseudo_au.py       # Pseudo-AU NME
│   └─ compute_au_mae.py          # AU MAE（OpenFace）
│
├─ utils/                   # ヘルパー関数
│   └─ estimate_offset.py         # 相互相関オフセット推定
│
├─ requirements.txt         # Python依存ライブラリ
└─ README.md                # このファイル
```

---

## 🛠️ 必要環境・インストール

```bash
# Python 3.8～3.10 推奨 (MediaPipe は <3.11)
pyenv install 3.10.12
pyenv local 3.10.12

# またはシステムの python3.10 を直接指定
env:
python3.10 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

**補足**

* mediapipe は Python >=3.8,<3.11 の環境でインストール可能
* FFmpeg / FFprobe（preprocessing）

---

## 🚀 実行手順

### 1. シフト値の算出

```bash
python evaluation/compute_dtw_min_diff.py \
  --real features/real.npy --gen features/gen.npy \
  --min_shift -30 --max_shift 30
# 出力例: Max DTW-norm ... at shift 16
```

### 2. 動画シフト

```bash
python preprocessing/shift_videos_trim.py \
  --real real_0804.mp4 --gen Receiver_0804.mp4 \
  --shift 16 --fps 30 \
  --out_real real_shifted.mp4 --out_gen Receiver_shifted.mp4
```

### 3. 前処理

```bash
python preprocessing/preprocess.py \
  --real real_shifted.mp4 --gen Receiver_shifted.mp4
```

### 4. ランドマーク抽出

```bash
python preprocessing/extract_landmarks.py \
  --aligned_dir frames/aligned/real --out_npy landmarks/real.npy
python preprocessing/extract_landmarks.py \
  --aligned_dir frames/aligned/gen  --out_npy landmarks/gen.npy
```

### 5. シーケンス特徴抽出

```bash
python preprocessing/extract_sequence_features.py \
  --aligned_real frames/aligned/real \
  --aligned_gen  frames/aligned/gen  --out_dir features
```

### 6. モデル準備・学習

#### 6.1 Deepfake検出器準備

```bash
python training/generate_detectors.py
```

#### 6.2 rPPGモデル学習

##### 6.2.1 特徴量・ラベルデータの作成例

以下の手順で `training/X_train.npy` と `training/y_train.npy` を準備できます。

```bash
# ステップ5のシーケンス特徴抽出実行後
python preprocessing/extract_sequence_features.py \
  --aligned_real frames/aligned/real \
  --aligned_gen  frames/aligned/gen \
  --out_dir features
# -> features ディレクトリに real.npy, gen.npy が生成される

# 特徴量とラベルを統合して X_train.npy, y_train.npy を生成
python - << 'EOS'
import numpy as np
# real.npy, gen.npy を読み込む
real = np.load('features/real.npy')
gen  = np.load('features/gen.npy')
# 特徴量行列を縦結合
X = np.vstack([real, gen])
# ラベルを作成 (0: 実写, 1: 生成)
y = np.hstack([np.zeros(len(real)), np.ones(len(gen))])
# trainingディレクトリへ保存
np.save('training/X_train.npy', X)
np.save('training/y_train.npy', y)
print('Saved X_train.npy', X.shape, 'y_train.npy', y.shape)
EOS
```

##### 6.2.2 学習実行

```bash
python training/generate_rppg_model.py \
  --features training/X_train.npy \
  --labels   training/y_train.npy
```

学習後、`training/rppg_model.pkl` が生成されます。

### 7. 指標計算

```bash
python evaluation/compute_fvd.py
python evaluation/compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy
python evaluation/compute_dscore.py
python evaluation/compute_dtw.py --real features/real.npy --gen features/gen.npy
python evaluation/compute_rppg.py --aligned_dir frames/aligned/gen --model training/rppg_model.pkl
python evaluation/compute_pseudo_au.py --real landmarks/real.npy --gen landmarks/gen.npy
# (オプション) OpenFace AU MAE
python evaluation/compute_au_mae.py
```

各スクリプトがターミナルに結果を出力します。

---

## 📈 開発メモ

* 精度改善: 検出器ファインチューニング、ランドマーク品質向上
* パラメータ調整: fps, grid\_size, patch\_size など
* 拡張案: GUI 化、自動レポート、本物の AU MAE
