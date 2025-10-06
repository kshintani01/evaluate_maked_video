# 🚀 ワンクリック実行ガイド

readmeの複雑な手順をワンクリックで実行できる統合スクリプトを作成しました。

## 📁 作成されたファイル

### 🤖 完全自動化版（推奨）
- `run_evaluation_pipeline_auto.py` - **完全自動化メインスクリプト**
- `quick_run_auto.sh` - **完全自動化シェルスクリプト**

### 📋 手動入力版（従来版）
- `run_evaluation_pipeline.py` - メインの統合スクリプト
- `quick_run.sh` - 簡単実行用シェルスクリプト

## 🎯 最も簡単な使用方法

### 🤖 完全自動化版（手動入力不要！）

```bash
# 🌟 真のワンクリック実行（推奨）
./quick_run_auto.sh real_0804.mp4 Receiver_0804.mp4

# 時間短縮版（FVDとモデル学習をスキップ）
./quick_run_auto.sh real_0804.mp4 Receiver_0804.mp4 --skip-fvd --skip-models
```

### 📋 従来版（DTWシフト値の手動入力が必要）

```bash
# シンプルな実行
./quick_run.sh real_0804.mp4 Receiver_0804.mp4

# 時間短縮版（FVDとモデル学習をスキップ）
./quick_run.sh real_0804.mp4 Receiver_0804.mp4 --skip-fvd --skip-models
```

## 🔧 詳細オプション付きの実行

```bash
# Pythonスクリプトを直接実行する場合
python run_evaluation_pipeline.py --real real_0804.mp4 --gen Receiver_0804.mp4

# 各種オプション付き
python run_evaluation_pipeline.py \
  --real real_0804.mp4 \
  --gen Receiver_0804.mp4 \
  --fps 30 \
  --min-shift -30 \
  --max-shift 30 \
  --skip-models \
  --skip-fvd
```

## 🎯 重要なポイント

### 1. 動画ファイル名の指定
- `--real`: 実写動画のファイル名
- `--gen`: 生成動画のファイル名

### 2. DTWによる動画のずれ調整

#### 🤖 完全自動化版
スクリプトが**完全自動**で以下を実行します：
1. 初回の特徴量抽出
2. **DTW最適化によるシフト値計算** ← 最重要
3. **DTW結果の自動解析とシフト値抽出** ← NEW！
4. シフト値に基づく動画調整
5. 調整後の評価指標計算

**✨ 手動入力は一切不要！真のワンクリック実行！**

#### 📋 従来版（手動入力が必要）
```
📝 最適シフト値を入力してください（例: -5, 0, 3など）: 
```
この表示が出たら、上に表示されたDTW計算結果から最適シフト値を確認して入力してください。

## ⚡ 時間短縮オプション

- `--skip-models`: Deepfake検出器とrPPGモデルの学習をスキップ
- `--skip-fvd`: FVD計算をスキップ（10-20分の時間短縮）

## 📊 実行される評価指標

1. **DTW (Dynamic Time Warping)** - 動画の時間同期評価
2. **NME (Normalized Mean Error)** - 顔ランドマークの精度
3. **D-Score** - Deepfake検出スコア
4. **FVD (Fréchet Video Distance)** - 動画品質評価
5. **Pseudo-AU NME** - Action Unit精度
6. **AU MAE** - Action Unit誤差
7. **rPPG Score** - 心拍数推定精度

## 🗂️ 出力ファイル

実行後、以下のファイルが生成されます：
- `real_shifted.mp4` / `gen_shifted.mp4` - シフト調整後の動画
- `landmarks/` - 顔ランドマークデータ
- `features/` - シーケンス特徴量
- `frames/` - 抽出されたフレーム画像
- `clips/` - FVD用クリップ

## ⚠️ 前提条件

1. 必要な依存関係がインストール済みであること
2. 指定した動画ファイルが存在すること
3. 十分なディスク容量があること（数GB推奨）

## 💡 トラブルシューティング

- エラーが発生した場合は、仮想環境が正しく設定されているか確認
- 動画ファイルのパスが正しいか確認
- 必要に応じて `requirements.txt` から依存関係を再インストール