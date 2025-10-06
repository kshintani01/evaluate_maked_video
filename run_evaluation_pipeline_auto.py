#!/usr/bin/env python3
"""
動画評価パイプライン統合実行スクリプト（完全自動化版）

DTWの結果を自動解析して、手動入力なしで完全自動実行します。
ユーザーの介入は一切不要で、真のワンクリック実行を実現します。
"""

import os
import sys
import subprocess
import argparse
import time
import re
from pathlib import Path
import shutil
import platform


def run_command(command, description="", check=True, capture_output=False):
    """コマンドを実行し、結果を表示（出力キャプチャ対応）"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"実行コマンド: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check,
            capture_output=capture_output, 
            text=True,
            encoding='utf-8' if platform.system() == "Windows" else None
        )
        if result.returncode == 0:
            print(f"✅ {description} - 完了")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ エラー: {description}")
        print(f"コマンド: {command}")
        print(f"終了コード: {e.returncode}")
        if capture_output and hasattr(e, 'stdout'):
            print(f"標準出力: {e.stdout}")
            print(f"標準エラー: {e.stderr}")
        if not check:
            print("⚠️  エラーを無視して続行します")
            return e
        else:
            raise


def extract_optimal_shift(dtw_output):
    """DTW計算結果から最適シフト値を自動抽出"""
    print("\n🤖 DTW結果を自動解析中...")
    
    # パターン1: "Min DTW-norm X.XXX at shift Y" を検索
    pattern1 = r"Min DTW-norm\s+[\d.]+\s+at\s+shift\s+(-?\d+)"
    match1 = re.search(pattern1, dtw_output)
    
    if match1:
        shift_value = int(match1.group(1))
        print(f"✅ 最適シフト値を自動検出: {shift_value}")
        return shift_value
    
    # パターン2: 全てのshift結果から最小値を検索
    pattern2 = r"Shift\s+(-?\d+):\s+DTW-norm\s+=\s+([\d.]+)"
    matches = re.findall(pattern2, dtw_output)
    
    if matches:
        best_shift = None
        best_norm = float('inf')
        
        print("📊 DTW評価結果:")
        for shift_str, norm_str in matches:
            shift = int(shift_str)
            norm = float(norm_str)
            print(f"   Shift {shift}: DTW-norm = {norm}")
            
            if norm < best_norm:
                best_norm = norm
                best_shift = shift
        
        if best_shift is not None:
            print(f"✅ 最適シフト値を自動算出: {best_shift} (DTW-norm: {best_norm})")
            return best_shift
    
    # パターン3: デフォルト値
    print("⚠️  DTW結果を解析できませんでした。デフォルト値 0 を使用します。")
    return 0


def create_directories():
    """必要なディレクトリを作成"""
    print("\n📁 必要なディレクトリを作成中...")
    
    directories = [
        "frames/raw/real",
        "frames/raw/gen", 
        "frames/aligned/real",
        "frames/aligned/gen",
        "clips/real",
        "clips/gen",
        "landmarks",
        "features",
        "features_tmp",
        "training"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")


def check_files_exist(real_video, gen_video):
    """動画ファイルの存在確認"""
    if not os.path.exists(real_video):
        raise FileNotFoundError(f"実写動画ファイルが見つかりません: {real_video}")
    if not os.path.exists(gen_video):
        raise FileNotFoundError(f"生成動画ファイルが見つかりません: {gen_video}")
    
    print(f"✅ 実写動画: {real_video}")
    print(f"✅ 生成動画: {gen_video}")


def get_python_command():
    """適切なPythonコマンドを取得"""
    if platform.system() == "Windows":
        python_commands = ["python", "python3", "py"]
    else:
        python_commands = ["python3", "python", "py"]
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🐍 使用するPythonコマンド: {cmd}")
                return cmd
        except FileNotFoundError:
            continue
    
    return "python"


def main():
    parser = argparse.ArgumentParser(
        description="動画評価パイプライン統合実行スクリプト（完全自動化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python run_evaluation_pipeline_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4
  python run_evaluation_pipeline_auto.py --real real_0804.mp4 --gen Receiver_0804.mp4 --skip-models
  
🤖 完全自動化: DTWシフト値の手動入力は不要です！
        """
    )
    
    parser.add_argument("--real", required=True, 
                       help="実写動画ファイル名 (例: real_0804.mp4)")
    parser.add_argument("--gen", required=True,
                       help="生成動画ファイル名 (例: Receiver_0804.mp4)")
    parser.add_argument("--fps", type=int, default=30,
                       help="フレームレート (デフォルト: 30)")
    parser.add_argument("--min-shift", type=int, default=-30,
                       help="DTW最小シフト値 (デフォルト: -30)")
    parser.add_argument("--max-shift", type=int, default=30,
                       help="DTW最大シフト値 (デフォルト: 30)")
    parser.add_argument("--skip-models", action="store_true",
                       help="モデル学習をスキップ（既存モデルを使用）")
    parser.add_argument("--skip-fvd", action="store_true",
                       help="FVD計算をスキップ（時間短縮）")
    
    args = parser.parse_args()
    
    print("🤖 動画評価パイプライン統合実行スクリプト（完全自動化版）")
    print(f"実行環境: {platform.system()} {platform.release()}")
    print(f"実写動画: {args.real}")
    print(f"生成動画: {args.gen}")
    print(f"フレームレート: {args.fps}")
    print(f"DTWシフト範囲: {args.min_shift} ～ {args.max_shift}")
    print("🎯 DTWシフト値は自動計算されます - 手動入力不要！")
    
    # 適切なPythonコマンドを取得
    python_cmd = get_python_command()
    
    try:
        # ファイル存在確認
        check_files_exist(args.real, args.gen)
        
        # ディレクトリ作成
        create_directories()
        
        # ==========================================
        # 1. 初回前処理
        # ==========================================
        run_command(
            f"{python_cmd} preprocessing/preprocess.py --real {args.real} --gen {args.gen}",
            "1. 動画のリサンプリング・フレーム抽出・空間アライン"
        )
        
        run_command(
            f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/real --out_npy landmarks/real_tmp.npy",
            "2. 実写動画の顔ランドマーク抽出"
        )
        
        run_command(
            f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/gen --out_npy landmarks/gen_tmp.npy", 
            "3. 生成動画の顔ランドマーク抽出"
        )
        
        run_command(
            f"{python_cmd} preprocessing/extract_sequence_features.py --aligned_real frames/aligned/real --aligned_gen frames/aligned/gen --out_dir features_tmp",
            "4. シーケンス特徴抽出（口/目開度）"
        )
        
        # ==========================================
        # 2. DTWによるシフト値算出（完全自動化）
        # ==========================================
        print("\n🤖 DTWによる動画のずれ調整 - 完全自動処理")
        dtw_result = run_command(
            f"{python_cmd} evaluation/compute_dtw_min_diff_improved.py --real features_tmp/real.npy --gen features_tmp/gen.npy --min_shift {args.min_shift} --max_shift {args.max_shift} --remove_invalid",
            "5. DTWシフト値の算出（改良版）",
            capture_output=True
        )
        
        # DTW出力を表示
        print("📊 DTW計算結果:")
        print(dtw_result.stdout)
        
        # 最適シフト値を自動抽出
        shift_value = extract_optimal_shift(dtw_result.stdout)
        
        print(f"\n🎯 自動決定されたシフト値: {shift_value} フレーム")
        if shift_value > 0:
            print(f"   → 実写動画が {shift_value} フレーム先行")
        elif shift_value < 0:
            print(f"   → 生成動画が {-shift_value} フレーム先行")
        else:
            print("   → 動画は同期済み")
        
        # ==========================================
        # 3. 動画シフト処理
        # ==========================================
        shifted_real = f"real_shifted.mp4"
        shifted_gen = f"gen_shifted.mp4"
        
        run_command(
            f"{python_cmd} preprocessing/shift_videos_trim.py --real {args.real} --gen {args.gen} --shift {shift_value} --fps {args.fps} --out-real {shifted_real} --out-gen {shifted_gen}",
            "6. 動画のシフト処理"
        )
        
        # ==========================================
        # 4. シフト後の前処理
        # ==========================================
        run_command(
            f"{python_cmd} preprocessing/preprocess.py --real {shifted_real} --gen {shifted_gen}",
            "7. シフト後のアライン済みフレーム抽出"
        )
        
        run_command(
            f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/real --out_npy landmarks/real.npy",
            "8. シフト後の実写動画顔ランドマーク抽出"
        )
        
        run_command(
            f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/gen --out_npy landmarks/gen.npy",
            "9. シフト後の生成動画顔ランドマーク抽出"
        )
        
        run_command(
            f"{python_cmd} preprocessing/extract_sequence_features.py --aligned_real frames/aligned/real --aligned_gen frames/aligned/gen --out_dir features",
            "10. シフト後のシーケンス特徴抽出"
        )
        
        if not args.skip_fvd:
            run_command(
                f"{python_cmd} preprocessing/clip_split.py",
                "11. FVD用クリップ生成"
            )
        
        # ==========================================
        # 5. モデル準備・学習（オプション）
        # ==========================================
        if not args.skip_models:
            run_command(
                f"{python_cmd} training/generate_detectors.py",
                "12. Deepfake検出器生成"
            )
            
            run_command(
                f"{python_cmd} training/train_detectors.py",
                "13. Deepfake検出器学習"
            )
            
            run_command(
                f"{python_cmd} utils/prepare_rppg_dataset.py --input-dir features --output-features training/X_train.npy --output-labels training/y_train.npy",
                "14. rPPG特徴量/ラベルデータ作成",
                check=False
            )
            
            run_command(
                f"{python_cmd} training/generate_rppg_model.py --features training/X_train.npy --labels training/y_train.npy",
                "15. rPPGモデル学習",
                check=False
            )
        else:
            print("\n⏭️  モデル学習をスキップしました")
        
        # ==========================================
        # 6. 評価指標の計算
        # ==========================================
        print("\n📊 評価指標の計算を開始します...")
        
        if not args.skip_fvd:
            run_command(
                f"{python_cmd} evaluation/compute_fvd.py",
                "16. FVD計算（10-20分かかります）"
            )
        else:
            print("\n⏭️  FVD計算をスキップしました")
        
        run_command(
            f"{python_cmd} evaluation/compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy",
            "17. NME計算"
        )
        
        run_command(
            f'{python_cmd} evaluation/compute_dscore.py --detectors detectors.pkl --real "frames/aligned/real/*.png" --gen "frames/aligned/gen/*.png"',
            "18. D-Score計算（3分程度）",
            check=False
        )
        
        run_command(
            f"{python_cmd} evaluation/compute_dtw.py --real features/real.npy --gen features/gen.npy",
            "19. DTW正規化距離計算"
        )
        
        run_command(
            f"{python_cmd} evaluation/compute_pseudo_au.py --real landmarks/real.npy --gen landmarks/gen.npy",
            "20. Pseudo-AU NME計算"
        )
        
        run_command(
            f"{python_cmd} evaluation/compute_au_mae.py",
            "21. AU MAE計算（オプション）",
            check=False
        )
        
        run_command(
            f"{python_cmd} evaluation/compute_rppg.py --aligned_dir frames/aligned/gen --model rppg_model.pkl",
            "22. rPPGスコア計算",
            check=False
        )
        
        # ==========================================
        # 完了メッセージ
        # ==========================================
        print("\n" + "="*60)
        print("🎉 動画評価パイプラインが完了しました！（完全自動化）")
        print("="*60)
        print(f"実行環境: {platform.system()}")
        print(f"実写動画: {args.real}")
        print(f"生成動画: {args.gen}")
        print(f"🤖 自動決定されたシフト値: {shift_value} フレーム")
        print(f"シフト後動画: {shifted_real}, {shifted_gen}")
        print("\n✨ 手動入力なしで全て自動実行されました！")
        print("📈 各評価指標の結果は上記の出力を確認してください。")
        print("📁 中間ファイルは以下のディレクトリに保存されています:")
        print("   - frames/: フレーム画像")
        print("   - landmarks/: 顔ランドマークデータ")
        print("   - features/: シーケンス特徴量")
        print("   - clips/: FVD用クリップ")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()