@echo off
chcp 65001 > nul

REM 動画評価パイプライン完全自動実行スクリプト (Windows版)
REM 🤖 DTWシフト値の手動入力は不要！完全自動化版

echo 🤖 動画評価パイプライン完全自動実行スクリプト (Windows版)
echo ==============================================
echo ✨ DTWシフト値を自動計算 - 手動入力不要！

REM 引数チェック
if "%2"=="" (
    echo 使用法: %0 ^<実写動画^> ^<生成動画^> [オプション]
    echo.
    echo 例:
    echo   %0 real_0804.mp4 Receiver_0804.mp4
    echo   %0 real_0804.mp4 Receiver_0804.mp4 --skip-fvd
    echo   %0 real_0804.mp4 Receiver_0804.mp4 --skip-models --skip-fvd
    echo.
    echo 🤖 完全自動化の特徴:
    echo   - DTWシフト値を自動計算・適用
    echo   - 手動入力は一切不要
    echo   - 真のワンクリック実行
    echo.
    echo 利用可能なオプション:
    echo   --skip-models : モデル学習をスキップ（既存モデル使用）
    echo   --skip-fvd    : FVD計算をスキップ（時間短縮）
    echo   --fps N       : フレームレート指定（デフォルト: 30）
    echo.
    pause
    exit /b 1
)

set REAL_VIDEO=%1
set GEN_VIDEO=%2
set OPTIONS=%3 %4 %5 %6 %7 %8 %9

echo 実写動画: %REAL_VIDEO%
echo 生成動画: %GEN_VIDEO%
echo オプション: %OPTIONS%
echo.

REM 仮想環境の確認と有効化
if exist "venv3.10\Scripts\activate.bat" (
    echo 🐍 仮想環境 venv3.10 を有効化します...
    call venv3.10\Scripts\activate.bat
) else if exist "venv312\Scripts\activate.bat" (
    echo 🐍 仮想環境 venv312 を有効化します...
    call venv312\Scripts\activate.bat
) else if exist "venv3.9\Scripts\activate.bat" (
    echo 🐍 仮想環境 venv3.9 を有効化します...
    call venv3.9\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo 🐍 仮想環境 venv を有効化します...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  仮想環境が見つかりません。システムのPythonを使用します。
)

REM 完全自動化Pythonスクリプト実行
echo 🤖 完全自動パイプラインを開始します...
echo ✨ DTWシフト値は自動計算されます - 待機不要！
python run_evaluation_pipeline_auto.py --real %REAL_VIDEO% --gen %GEN_VIDEO% %OPTIONS%

echo.
echo 🎉 完全自動処理完了！
echo 🤖 手動入力なしで全て自動実行されました！
pause