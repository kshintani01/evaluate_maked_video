# 生成動画評価パイプライン

本プロジェクトは、実写動画と生成動画を比較し、6つの評価指標を一貫して算出するパイプラインです。各ステップをスクリプト化し、独立して実行・テストできる構成になっています。

## 🔧 **最新の改良点**
- **顔検出エラーの修正**: `.DS_Store`等の非画像ファイルによるOpenCVエラーを解決
- **DTW評価の高精度化**: 無効フレームの自動除去により、より正確な同期評価を実現
- **ロバストな前処理**: エラーハンドリングと警告システムを強化

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
│   ├─ compute_dtw_min_diff.py    # DTWシフト最適化（基本版）
│   ├─ compute_dtw_min_diff_improved.py # DTWシフト最適化（改良版）⭐
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

# 仮想環境の作成と有効化
python3.10 -m venv venv3.10
source venv3.10/bin/activate

# パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt
```

**必要な外部ツール**
- FFmpeg / FFprobe（動画処理用）
- OpenCV 4.x（画像処理用）

**重要な依存関係**
- `mediapipe`: Python >=3.8,<3.11 の環境でのみ動作
- `dtw-python`: DTW距離計算用
- `tensorflow`: Mediapipeの内部で使用

---

## 🚀 実行手順

以下の順序で処理を実行してください。

### 前処理前のディレクトリ作成
以下の6つのディレクトリをあらかじめ作成してください。

```bash
mkdir -p frames/raw/real \
frames/raw/gen \
frames/aligned/real \
frames/aligned/gen \
clips/real \
clips/gen
```

### 1. 前処理

1. 動画のリサンプリング・フレーム抽出・空間アライン

```bash
python preprocessing/preprocess.py --real real_0804.mp4 --gen Receiver_0804.mp4
```

2. 顔ランドマーク抽出

```bash
python preprocessing/extract_landmarks.py --aligned_dir frames/aligned/real --out_npy landmarks/real_tmp.npy
python preprocessing/extract_landmarks.py --aligned_dir frames/aligned/gen  --out_npy landmarks/gen_tmp.npy
```

3. シーケンス特徴抽出（口/目開度など）

```bash
python preprocessing/extract_sequence_features.py --aligned_real frames/aligned/real --aligned_gen  frames/aligned/gen  --out_dir features_tmp
```

### 2. シフト値の算出

**⭐ 推奨：改良版DTW評価**
```bash
python evaluation/compute_dtw_min_diff_improved.py \
  --real features_tmp/real.npy \
  --gen features_tmp/gen.npy \
  --min_shift -30 --max_shift 30 \
  --remove_invalid
```

**従来版（参考）**
```bash
python evaluation/compute_dtw_min_diff.py --real features_tmp/real.npy --gen features_tmp/gen.npy --min_shift -30 --max_shift 30
```

**改良版の利点:**
- 無効な顔検出フレーム（`[0,0]`）を自動除去
- より正確な同期評価（通常は数フレーム以内の精度）
- 詳細な統計情報とシーケンス長の表示

### 3. 動画シフト

```bash
python preprocessing/shift_videos_trim.py --real real_0804.mp4 --gen Receiver_0804.mp4 --shift <上記で得たシフト値> --fps 30 --out-real real_shifted.mp4 --out-gen Receiver_shifted.mp4
```

### 4. シフト後の前処理

1. アライン済みフレーム抽出

```bash
python preprocessing/preprocess.py --real real_shifted.mp4 --gen Receiver_shifted.mp4
```

2. 顔ランドマーク再抽出

```bash
python preprocessing/extract_landmarks.py --aligned_dir frames/aligned/real --out_npy landmarks/real.npy
python preprocessing/extract_landmarks.py --aligned_dir frames/aligned/gen  --out_npy landmarks/gen.npy
```

3. シーケンス再特徴抽出（口/目開度など）

```bash
python preprocessing/extract_sequence_features.py --aligned_real frames/aligned/real --aligned_gen  frames/aligned/gen  --out_dir features
```

4. FVD用クリップ生成

```bash
python preprocessing/clip_split.py
```

### 5. モデル準備・学習

#### 5.1 Deepfake検出器準備

```bash
python training/generate_detectors.py
python training/train_detectors.py
```

#### 5.2 rPPGモデル学習

1. 特徴量/ラベルデータを作成

```bash
python utils/prepare_rppg_dataset.py --input-dir features --output-features training/X_train.npy --output-labels training/y_train.npy
```
2. 学習実行

```bash
python training/generate_rppg_model.py --features training/X_train.npy --labels training/y_train.npy
```

### 6. 評価指標の計算

```bash
python evaluation/compute_fvd.py # 10-20分かかります
python evaluation/compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy
python evaluation/compute_dscore.py --detectors detectors.pkl --real "frames/aligned/real/*.png" --gen "frames/aligned/gen/*.png" # 3分程度かかります
python evaluation/compute_dtw.py --real features/real.npy --gen features/gen.npy
python evaluation/compute_pseudo_au.py --real landmarks/real.npy --gen landmarks/gen.npy
# (オプション) AU MAE
python evaluation/compute_au_mae.py
# 現在、動作しない
python evaluation/compute_rppg.py --aligned_dir frames/aligned/gen --model rppg_model.pkl
```

各スクリプトがターミナルに結果を出力します。

---

## � 評価指標の詳細

### DTW（Dynamic Time Warping）評価
- **目的**: 2つの動画間の時間同期のずれを検出
- **特徴量**: 口の開度（上唇-下唇間距離）、目の開度（上瞼-下瞼間距離）
- **出力**: 最適シフト値（フレーム数）とDTW正規化距離

### 改良版DTWの特徴
- **無効フレーム除去**: 顔検出に失敗したフレーム（特徴量が`[0,0]`）を自動除去
- **高精度評価**: 有効フレームのみを使用することで、数フレーム単位の精密な同期評価
- **詳細出力**: シーケンス長、有効フレーム数、最適化過程を表示

### 期待される結果
- **良好な同期**: ±3フレーム以内（約0.1秒@30fps）
- **軽微な遅延**: ±10フレーム以内（約0.33秒@30fps）
- **大きなずれ**: ±30フレーム以上（1秒以上）

## ⚠️ トラブルシューティング

### よくある問題と解決法

1. **`cv2.error: !_src.empty()`エラー**
   - 原因: `.DS_Store`等の非画像ファイルの読み込み
   - 解決: 改良版のスクリプトを使用（自動フィルタリング）

2. **顔検出失敗が多い**
   - 原因: 照明条件、画質、顔の向き
   - 対策: 入力動画の品質改善、MediaPipeのパラメータ調整

3. **DTW評価で大きなシフト値**
   - 原因: 無効フレームによる誤った評価
   - 解決: `--remove_invalid`オプションを使用

## 📈 開発メモ

### 完了した改良
- ✅ 顔検出エラーの修正（OpenCVエラー対応）
- ✅ DTW評価の高精度化（無効フレーム除去）
- ✅ エラーハンドリングの強化

### 今後の改善案
- 📝 GUI化による操作性向上
- 📝 自動レポート生成機能
- 📝 統計的有意性検定の追加
- 📝 可視化機能（DTW距離のプロット等）
- 📝 バッチ処理機能（複数動画の一括評価）