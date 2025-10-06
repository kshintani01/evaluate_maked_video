# 🚀 Windows版 ワンクリック実行ガイド

Windows環境でreadmeの複雑な手順をワンクリックで実行できる統合スクリプトです。

## 📁 Windows用ファイル

### 🤖 完全自動化版（推奨）
- `run_evaluation_pipeline_auto.py` - **完全自動化メインスクリプト**（クロスプラットフォーム）
- `run_evaluation_pipeline_windows_auto.py` - **Windows専用完全自動化スクリプト**（推奨）
- `quick_run_auto.bat` - **完全自動化バッチファイル**

### 📋 手動入力版（従来版）
- `run_evaluation_pipeline_windows.py` - Windows対応メインスクリプト
- `quick_run.bat` - Windows用バッチファイル

## 🎯 最も簡単な使用方法

### 🤖 完全自動化版（手動入力不要！）

```cmd
# 🌟 Windows専用完全自動化版（最も推奨）
python run_evaluation_pipeline_windows_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4

# クロスプラットフォーム版
python run_evaluation_pipeline_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4

# バッチファイル版
.\quick_run_auto.bat real_0804.mp4 Receiver_0804.mp4

# 時間短縮版（FVDとモデル学習をスキップ）
python run_evaluation_pipeline_windows_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4 --skip-fvd --skip-models
```

### 📋 従来版（DTWシフト値の手動入力が必要）

```cmd
# シンプルな実行
quick_run.bat real_0804.mp4 Receiver_0804.mp4

# 時間短縮版（FVDとモデル学習をスキップ）
quick_run.bat real_0804.mp4 Receiver_0804.mp4 --skip-fvd --skip-models
```

### Pythonスクリプトを直接実行

#### 🤖 完全自動化版
```cmd
# 完全自動実行（手動入力不要）
python run_evaluation_pipeline_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4

# オプション付き完全自動実行
python run_evaluation_pipeline_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4 --skip-models --skip-fvd
```

#### 📋 従来版
```cmd
# 基本実行（DTWシフト値の手動入力が必要）
python run_evaluation_pipeline_windows.py --real real_0804.mp4 --gen Receiver_0804.mp4

# オプション付き実行
python run_evaluation_pipeline_windows.py --real real_0804.mp4 --gen Receiver_0804.mp4 --skip-models --skip-fvd
```

## 🔧 Windows特有の対応

### 1. 文字エンコーディング
- UTF-8対応済み（日本語ファイル名・パス対応）
- バッチファイルでは`chcp 65001`で文字化け防止

### 2. Pythonコマンド自動検出
- `python`, `python3`, `py`コマンドを自動検出
- Windows環境に合わせて最適なコマンドを選択

### 3. 仮想環境対応
Windows用の仮想環境パスを自動検出：
- `venv3.10\Scripts\activate.bat`
- `venv312\Scripts\activate.bat` 
- `venv3.9\Scripts\activate.bat`
- `venv\Scripts\activate.bat`

### 4. パス区切り文字
- Windows環境でのバックスラッシュ`\`に対応
- `pathlib.Path`を使用してOS非依存のパス処理

### 5. 🤖 完全自動化対応（NEW！）
- **DTW結果の自動解析**: 正規表現で最適シフト値を抽出
- **手動入力完全排除**: ユーザーの待機時間ゼロ
- **真のワンクリック実行**: バッチファイル実行だけで完了

## ⚠️ Windows環境での前提条件

### 1. Python環境
```cmd
# Pythonのバージョン確認
python --version
# または
python3 --version
# または
py --version
```

### 2. 必要なツール
- **FFmpeg**: [公式サイト](https://ffmpeg.org/download.html)からダウンロード
  - `ffmpeg.exe`がPATHに通っていることを確認
- **Git** (オプション): リポジトリ管理用

### 3. 依存関係のインストール
```cmd
# 仮想環境作成（推奨）
python -m venv venv
venv\Scripts\activate

# パッケージインストール
pip install --upgrade pip
pip install -r requirements.txt
```

## 🚀 実行手順

### 1. コマンドプロンプトを開く
- Windows キー + R → `cmd` と入力してEnter
- または PowerShell を使用

### 2. プロジェクトディレクトリに移動
```cmd
cd "C:\path\to\your\project\generated_movie"
```

### 3. スクリプト実行
```cmd
quick_run.bat real_0804.mp4 Receiver_0804.mp4
```

## � エラー対処法

### 1. "quick_run_auto.bat is not recognized" エラー
```cmd
# 解決法1: 相対パスで実行
.\quick_run_auto.bat real_0804.mp4 Receiver_0804.mp4

# 解決法2: 直接Pythonスクリプト実行（推奨）
python run_evaluation_pipeline_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4
```

### 2. "expected string or bytes-like object, got NoneType" エラー
DTWシフト値計算で発生する場合：
```cmd
# 手動でDTW計算を実行して確認
python evaluation/compute_dtw_min_diff_improved.py --real features_tmp/real.npy --gen features_tmp/gen.npy --min_shift -30 --max_shift 30 --remove_invalid
```
- 改良版スクリプトは自動でデフォルト値0を使用して続行します

## �💡 Windows特有のトラブルシューティング

### 3. 文字化けが発生する場合
```cmd
chcp 65001
```
でUTF-8に設定してから実行

### 4. FFmpegが見つからない場合
```cmd
# FFmpegのインストール確認
ffmpeg -version
```
PATHが通っていない場合は環境変数に追加

### 5. 権限エラーが発生する場合
- 管理者権限でコマンドプロンプトを実行
- または、ユーザーディレクトリ内でファイルを実行

### 6. 長いパス名でエラーが発生する場合
Windows 10/11で長いパス名を有効化：
1. グループポリシー → コンピューターの構成 → 管理用テンプレート → システム → ファイルシステム
2. 「Win32 長いパスを有効にする」を有効化

## 📊 実行される評価指標（Windows版）

macOS/Linux版と同じ評価指標が実行されます：
1. **DTW (Dynamic Time Warping)** - 動画の時間同期評価
2. **NME (Normalized Mean Error)** - 顔ランドマークの精度
3. **D-Score** - Deepfake検出スコア
4. **FVD (Fréchet Video Distance)** - 動画品質評価
5. **Pseudo-AU NME** - Action Unit精度
6. **AU MAE** - Action Unit誤差
7. **rPPG Score** - 心拍数推定精度

## 🗂️ 出力ファイル（Windows版）

実行後、以下のファイルが生成されます：
- `real_shifted.mp4` / `gen_shifted.mp4` - シフト調整後の動画
- `landmarks\` - 顔ランドマークデータ
- `features\` - シーケンス特徴量
- `frames\` - 抽出されたフレーム画像
- `clips\` - FVD用クリップ

## 🤖 完全自動化版の特徴

| 項目 | 従来版 | 🤖 完全自動化版 |
|------|--------|-----------------|
| **DTW計算** | ✅ 自動実行 | ✅ 自動実行 |
| **シフト値抽出** | ❌ 手動入力必要 | ✅ **自動解析・抽出** |
| **動画調整** | ✅ 自動実行 | ✅ 自動実行 |
| **評価指標計算** | ✅ 自動実行 | ✅ 自動実行 |
| **ユーザー操作** | � シフト値入力待ち | 🤖 **完全無人実行** |

### 自動化の仕組み
1. **DTW結果をキャプチャ** - コマンド出力を自動取得
2. **正規表現による解析** - 「Min DTW-norm X.XXX at shift Y」パターンを検出
3. **最適値の自動抽出** - シフト値を自動で数値として抽出
4. **フォールバック処理** - 解析失敗時はデフォルト値0を使用

## �🔄 macOS/Linux版との互換性

- 同じPythonスクリプトが両OS で動作
- プラットフォーム自動検出により適切なコマンド選択
- ファイルパス処理がOS非依存
- **完全自動化機能も両OS対応**