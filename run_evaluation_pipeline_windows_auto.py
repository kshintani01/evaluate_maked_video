#!/usr/bin/env python3
"""
動画評価パイプライン統合実行スクリプト（Windows完全自動化版）

Windows環境でDTWシフト値を確実に自動抽出する特別版です。
"""

import os
import sys
import subprocess
import argparse
import time
import re
import tempfile
from pathlib import Path
import shutil
import platform


def run_command_with_output(command, description=""):
    """コマンドを実行して出力を確実にキャプチャ（Windows特化）"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"実行コマンド: {command}")
    print(f"{'='*60}")
    
    try:
        # Windows環境での確実な出力キャプチャ
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # エンコーディングエラーを置換
        )
        
        # 標準出力と標準エラー出力を結合
        combined_output = ""
        if result.stdout:
            combined_output += result.stdout
            print("📤 標準出力:")
            print(result.stdout)
        
        if result.stderr:
            combined_output += "\n" + result.stderr
            print("⚠️ 標準エラー出力:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - 完了")
        else:
            print(f"⚠️ {description} - 警告（終了コード: {result.returncode}）")
        
        return combined_output, result.returncode
        
    except Exception as e:
        print(f"❌ エラー: {description}")
        print(f"例外: {e}")
        return str(e), 1


def run_command(command, description="", check=True):
    """通常のコマンド実行（出力キャプチャなし）"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"実行コマンド: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check,
            text=True,
            encoding='utf-8'
        )
        if result.returncode == 0:
            print(f"✅ {description} - 完了")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ エラー: {description}")
        print(f"コマンド: {command}")
        print(f"終了コード: {e.returncode}")
        if not check:
            print("⚠️  エラーを無視して続行します")
            return e
        else:
            raise


def extract_optimal_shift_windows(dtw_output):
    """Windows環境でDTW結果から最適シフト値を抽出"""
    print("\n🤖 DTW結果を自動解析中（Windows特化版）...")
    
    # 出力の確認
    if not dtw_output or len(dtw_output.strip()) == 0:
        print("⚠️  DTW出力が空です。デフォルト値 0 を使用します。")
        return 0
    
    print("📋 DTW出力内容（デバッグ用）:")
    print("-" * 40)
    print(dtw_output)
    print("-" * 40)
    
    # パターン1: "Min DTW-norm X.XXX at shift Y" を検索
    patterns = [
        r"Min DTW-norm\s+([\d.]+)\s+at\s+shift\s+(-?\d+)",
        r"最小DTW正規化距離\s+([\d.]+)\s+シフト\s+(-?\d+)",
        r"shift\s+(-?\d+).*DTW-norm\s*=\s*([\d.]+)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, dtw_output, re.IGNORECASE)
        if matches:
            if len(matches[0]) == 2:
                try:
                    if pattern == patterns[2]:  # shift が最初の場合
                        shift_value = int(matches[0][0])
                        dtw_norm = float(matches[0][1])
                    else:  # norm が最初の場合
                        dtw_norm = float(matches[0][0])
                        shift_value = int(matches[0][1])
                    
                    print(f"✅ 最適シフト値を自動検出: {shift_value} (DTW-norm: {dtw_norm})")
                    return shift_value
                except (ValueError, IndexError) as e:
                    print(f"⚠️ パターンマッチはしたが値の変換に失敗: {e}")
                    continue
    
    # パターン2: 全てのshift結果から最小値を検索
    shift_patterns = [
        r"Shift\s+(-?\d+):\s+DTW-norm\s*=\s*([\d.]+)",
        r"シフト\s+(-?\d+):\s+DTW正規化距離\s*=\s*([\d.]+)"
    ]
    
    all_results = []
    for pattern in shift_patterns:
        matches = re.findall(pattern, dtw_output, re.IGNORECASE)
        all_results.extend(matches)
    
    if all_results:
        best_shift = None
        best_norm = float('inf')
        
        print("📊 DTW評価結果:")
        valid_results = []
        
        for shift_str, norm_str in all_results:
            try:
                shift = int(shift_str)
                norm = float(norm_str)
                valid_results.append((shift, norm))
                print(f"   Shift {shift}: DTW-norm = {norm}")
                
                if norm < best_norm:
                    best_norm = norm
                    best_shift = shift
            except (ValueError, TypeError):
                continue
        
        if best_shift is not None and valid_results:
            print(f"✅ 最適シフト値を自動算出: {best_shift} (DTW-norm: {best_norm})")
            return best_shift
    
    # パターン3: 行ごとに解析
    lines = dtw_output.split('\n')
    for line in lines:
        # "→ Real video leads by X frames" パターン
        if "real video leads" in line.lower() or "実写動画が" in line:
            numbers = re.findall(r'(-?\d+)', line)
            if numbers:
                try:
                    shift_value = int(numbers[0])
                    print(f"✅ リードフレーム情報から抽出: {shift_value}")
                    return shift_value
                except ValueError:
                    continue
        
        # "Generated video leads" パターン
        if "generated video leads" in line.lower() or "生成動画が" in line:
            numbers = re.findall(r'(-?\d+)', line)
            if numbers:
                try:
                    shift_value = -int(numbers[0])  # 符号を反転
                    print(f"✅ リードフレーム情報から抽出: {shift_value}")
                    return shift_value
                except ValueError:
                    continue
    
    # デフォルト値
    print("⚠️  DTW結果を解析できませんでした。デフォルト値 0 を使用します。")
    print("💡 手動でDTWスクリプトを実行して結果を確認してください:")
    print("   python evaluation/compute_dtw_min_diff_improved.py --real features_tmp/real.npy --gen features_tmp/gen.npy --min_shift -30 --max_shift 30 --remove_invalid")
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
    python_commands = ["python", "python3", "py"]
    
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
        description="動画評価パイプライン統合実行スクリプト（Windows完全自動化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--real", required=True, 
                       help="実写動画ファイル名")
    parser.add_argument("--gen", required=True,
                       help="生成動画ファイル名")
    parser.add_argument("--fps", type=int, default=30,
                       help="フレームレート")
    parser.add_argument("--min-shift", type=int, default=-30,
                       help="DTW最小シフト値")
    parser.add_argument("--max-shift", type=int, default=30,
                       help="DTW最大シフト値")
    parser.add_argument("--skip-models", action="store_true",
                       help="モデル学習をスキップ")
    parser.add_argument("--skip-fvd", action="store_true",
                       help="FVD計算をスキップ")
    
    args = parser.parse_args()
    
    print("🤖 動画評価パイプライン（Windows完全自動化版）")
    print(f"実行環境: {platform.system()} {platform.release()}")
    print(f"実写動画: {args.real}")
    print(f"生成動画: {args.gen}")
    print("🎯 DTWシフト値は完全自動で計算されます！")
    
    python_cmd = get_python_command()
    
    try:
        check_files_exist(args.real, args.gen)
        create_directories()
        
        # 前処理
        run_command(f"{python_cmd} preprocessing/preprocess.py --real {args.real} --gen {args.gen}",
                   "1. 動画の前処理")
        
        run_command(f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/real --out_npy landmarks/real_tmp.npy",
                   "2. 実写動画ランドマーク抽出")
        
        run_command(f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/gen --out_npy landmarks/gen_tmp.npy",
                   "3. 生成動画ランドマーク抽出")
        
        run_command(f"{python_cmd} preprocessing/extract_sequence_features.py --aligned_real frames/aligned/real --aligned_gen frames/aligned/gen --out_dir features_tmp",
                   "4. 特徴量抽出")
        
        # DTW計算（完全自動化）
        print("\n🤖 DTWによる動画のずれ調整 - Windows完全自動処理")
        dtw_output, return_code = run_command_with_output(
            f"{python_cmd} evaluation/compute_dtw_min_diff_improved.py --real features_tmp/real.npy --gen features_tmp/gen.npy --min_shift {args.min_shift} --max_shift {args.max_shift} --remove_invalid",
            "5. DTWシフト値の算出"
        )
        
        # シフト値の自動抽出
        shift_value = extract_optimal_shift_windows(dtw_output)
        
        print(f"\n🎯 自動決定されたシフト値: {shift_value} フレーム")
        if shift_value > 0:
            print(f"   → 実写動画が {shift_value} フレーム先行")
        elif shift_value < 0:
            print(f"   → 生成動画が {-shift_value} フレーム先行")
        else:
            print("   → 動画は同期済み")
        
        # 動画シフト処理
        shifted_real = "real_shifted.mp4"
        shifted_gen = "gen_shifted.mp4"
        
        run_command(f"{python_cmd} preprocessing/shift_videos_trim.py --real {args.real} --gen {args.gen} --shift {shift_value} --fps {args.fps} --out-real {shifted_real} --out-gen {shifted_gen}",
                   "6. 動画シフト処理")
        
        # シフト後の処理
        run_command(f"{python_cmd} preprocessing/preprocess.py --real {shifted_real} --gen {shifted_gen}",
                   "7. シフト後前処理")
        
        run_command(f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/real --out_npy landmarks/real.npy",
                   "8. シフト後実写ランドマーク抽出")
        
        run_command(f"{python_cmd} preprocessing/extract_landmarks.py --aligned_dir frames/aligned/gen --out_npy landmarks/gen.npy",
                   "9. シフト後生成ランドマーク抽出")
        
        run_command(f"{python_cmd} preprocessing/extract_sequence_features.py --aligned_real frames/aligned/real --aligned_gen frames/aligned/gen --out_dir features",
                   "10. シフト後特徴量抽出")
        
        if not args.skip_fvd:
            run_command(f"{python_cmd} preprocessing/clip_split.py", "11. FVD用クリップ生成")
        
        # 評価指標計算（簡略版）
        print("\n📊 評価指標の計算...")
        
        run_command(f"{python_cmd} evaluation/compute_nme.py --real landmarks/real.npy --gen landmarks/gen.npy",
                   "NME計算", check=False)
        
        run_command(f"{python_cmd} evaluation/compute_dtw.py --real features/real.npy --gen features/gen.npy",
                   "DTW正規化距離計算", check=False)
        
        run_command(f"{python_cmd} evaluation/compute_pseudo_au.py --real landmarks/real.npy --gen landmarks/gen.npy",
                   "Pseudo-AU NME計算", check=False)
        
        print(f"\n🎉 Windows完全自動処理完了！")
        print(f"🤖 自動決定シフト値: {shift_value} フレーム")
        print(f"シフト後動画: {shifted_real}, {shifted_gen}")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()