# 🚀 Windows版 ワンクリック実行ガイド

Windows環境でreadmeの複雑な手順をワンクリックで実行できる統合スクリプトです。

## 📁 Windows用ファイル

- `run_evaluation_pipeline_windows.py` - Windows対応メインスクリプト
- `quick_run.bat` - Windows用バッチファイル

## 🎯 最も簡単な使用方法

### コマンドプロンプト/PowerShellから実行

```cmd
# シンプルな実行（推奨）
quick_run.bat real_0804.mp4 Receiver_0804.mp4

# 時間短縮版（FVDとモデル学習をスキップ）
quick_run.bat real_0804.mp4 Receiver_0804.mp4 --skip-fvd --skip-models
```

### Pythonスクリプトを直接実行

```cmd
# 基本実行
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

## 💡 Windows特有のトラブルシューティング

### 1. 文字化けが発生する場合
```cmd
chcp 65001
```
でUTF-8に設定してから実行

### 2. FFmpegが見つからない場合
```cmd
# FFmpegのインストール確認
ffmpeg -version
```
PATHが通っていない場合は環境変数に追加

### 3. 権限エラーが発生する場合
- 管理者権限でコマンドプロンプトを実行
- または、ユーザーディレクトリ内でファイルを実行

### 4. 長いパス名でエラーが発生する場合
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

## 🔄 macOS/Linux版との互換性

- 同じPythonスクリプトが両OS で動作
- プラットフォーム自動検出により適切なコマンド選択
- ファイルパス処理がOS非依存