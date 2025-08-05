# Real Communication 動画評価パイプライン

本プロジェクトは、実写動画と生成動画を比較し、6つの評価指標を一貫して算出するパイプラインです。各ステップをスクリプト化し、独立して実行・テストできる構成になっています。

---

## 📋 構成ファイル一覧

| ファイル名 | 説明 |
| ----- | -- |
|       |    |

| **requirements.txt**               | Python ライブラリ依存一覧                                         |
| ---------------------------------- | -------------------------------------------------------- |
| **shift\_videos\_trim.py**         | 動画をフレーム単位でトリミング（シフト）                                     |
| **preprocess.py**                  | 前処理：リサンプル・フレーム抽出・空間アライン・クリップ保存                           |
| **extract\_landmarks.py**          | アライン済フレームから MediaPipe 顔ランドマークを抽出                         |
| **extract\_sequence\_features.py** | アライン済フレームから口開度・目開度時系列を抽出                                 |
| **detectors.py**                   | Deepfake 検出器モデル定義（timm）                                  |
| **generate\_detectors.py**         | 検出器モデルを pickle 化して `detectors.pkl` を作成                   |
| **generate\_rppg\_features.py**    | トレーニング用 rPPG 特徴量とラベル（`X_train.npy`, `y_train.npy`）生成     |
| **generate\_rppg\_model.py**       | rPPG 特徴量から LogisticRegression モデル (`rppg_model.pkl`) を学習 |
| **compute\_fvd.py**                | FVD（Fréchet Video Distance）計算                            |
| **compute\_nme.py**                | NME（Normalized Mean Error）計算                             |
| **compute\_dscore.py**             | D-Score（Deepfake Detector Confidence）計算                  |
| **compute\_dtw\_max\_diff.py**     | DTW-norm をシフトごとに計算し最大値を表示                                |
| **compute\_rppg.py**               | rPPG Realness Score 計算                                   |
| **compute\_pseudo\_au.py**         | 疑似 AU NME（口・目開閉忠実度）計算                                    |

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

- FFmpeg, FFprobe（`preprocess.py`, `shift_videos_trim.py` で使用）
- MediaPipe（顔ランドマーク検出）

---

## 🚀 実行手順（例）

### 1. 動画シフト

```bash
python shift_videos_trim.py \
  --real real_0804.mp4 \
  --gen  Receiver_0804.mp4 \
  --shift 16 --fps 30 \
  --out_real real_shifted.mp4 \
  --out_gen  Receiver_shifted.mp4
```

### 2. 前処理

```bash
python preprocess.py \
  --real real_shifted.mp4 \
  --gen  Receiver_shifted.mp4
```

### 3. ランドマーク抽出

```bash
python extract_landmarks.py \
  --aligned_dir frames/aligned/real --out_npy landmarks/real.npy
python extract_landmarks.py \
  --aligned_dir frames/aligned/gen  --out_npy landmarks/gen.npy
```

### 4. シーケンス特徴抽出

```bash
python extract_sequence_features.py \
  --aligned_real frames/aligned/real \
  --aligned_gen  frames/aligned/gen  \
  --out_dir      features
```

### 5. Deepfake 検出モデル準備

```bash
python generate_detectors.py
# detectors.pkl が生成される
```

### 6. rPPG モデル学習

```bash
python generate_rppg_features.py \
  --real_dir real_videos --gen_dir gen_videos \
  --out_features X_train.npy --out_labels y_train.npy
python generate_rppg_model.py \
  --features X_train.npy --labels y_train.npy
```

### 7. 指標計算

```bash
python compute_fvd.py
python compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy
python compute_dscore.py
python compute_dtw_max_diff.py --real features/real.npy --gen features/gen.npy --min_shift -20 --max_shift 20
python compute_rppg.py --aligned_dir frames/aligned/gen --model rppg_model.pkl
python compute_pseudo_au.py --real landmarks/real.npy --gen landmarks/gen.npy
```

**実行結果** に応じて、各スクリプトが評価指標をターミナルに出力します。

---

## 📈 開発メモ

- **精度改善**: `compute_nme.py` のランドマーク検出品質向上、`compute_dscore.py` 用検出器モデルのファインチューニングなど。
- **パラメータ調整**: `preprocess.py` のリサンプル解像度／fps、`compute_rppg.py` のパッチ設定など。
- **拡張案**: 本来の OpenFace AU MAE に対応する `compute_au_mae.py` の復活、GUI 化、ベンチマーク自動レポート。

---

README.md をコミット後、GitHub リポジトリにプッシュしてください。

