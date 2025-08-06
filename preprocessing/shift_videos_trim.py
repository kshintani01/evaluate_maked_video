#!/usr/bin/env python3
# shift_videos_trim.py (改良版)

import argparse
import subprocess
import sys

def run_cmd(cmd):
    print(f"[DEBUG] running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg failed: {e}")
        sys.exit(1)

def get_duration(path):
    # ffprobe で秒数を取得
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        path
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout)

def trim_and_encode(input_path, output_path, trim_frames, fps, crf, bitrate, keep_audio):
    # 先頭 trim_frames フレームを秒数に変換
    start = trim_frames / fps
    # 入力全長取得
    total = get_duration(input_path)
    # 切り落とし後の長さ
    duration = total - start
    # FFmpeg コマンド組み立て
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-ss', str(start), '-i', input_path,
        '-t', str(duration),
        '-c:v', 'libx264', '-preset', 'fast',
        '-crf', str(crf),
    ]
    if bitrate:
        cmd += ['-b:v', bitrate]
    if not keep_audio:
        cmd += ['-an']
    else:
        cmd += ['-c:a', 'copy']
    cmd += [output_path]

    run_cmd(cmd)

def main():
    p = argparse.ArgumentParser(description="Trim videos by frame offset and align lengths")
    p.add_argument('--real',    required=True, help='Path to real video')
    p.add_argument('--gen',     required=True, help='Path to generated video')
    p.add_argument('--shift',   type=int,   required=True,
                   help='Frame shift: positive→realから、negative→genからトリム')
    p.add_argument('--fps',     type=int,   default=30, help='Frame rate')
    p.add_argument('--crf',     type=int,   default=23, help='x264 Quality (lower=高画質)')
    p.add_argument('--bitrate', type=str,   default=None,
                   help='Video bitrate (e.g. 2M), 指定しない場合はCRFのみ')
    p.add_argument('--keep-audio', action='store_true',
                   help='音声を残す場合に指定（デフォルト: 音声削除）')
    p.add_argument('--out-real', required=True, help='Output path for real')
    p.add_argument('--out-gen',  required=True, help='Output path for gen')
    args = p.parse_args()

    # 切り落とし先を判断
    if args.shift >= 0:
        # real をトリム、gen は全長
        trim_and_encode(args.real, args.out_real,
                        args.shift, args.fps,
                        args.crf, args.bitrate, args.keep_audio)
        # gen も同じ長さに揃えて再エンコード
        dur = get_duration(args.out_real)
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', args.gen, '-t', str(dur),
            '-c:v', 'libx264', '-preset', 'fast',
            '-crf', str(args.crf)
        ]
        if args.bitrate:
            cmd += ['-b:v', args.bitrate]
        if not args.keep_audio:
            cmd += ['-an']
        else:
            cmd += ['-c:a', 'copy']
        cmd += [args.out_gen]
        run_cmd(cmd)
    else:
        # gen をトリム、real は全長
        trim_and_encode(args.gen, args.out_gen,
                        -args.shift, args.fps,
                        args.crf, args.bitrate, args.keep_audio)
        # real を同じ長さに揃える
        dur = get_duration(args.out_gen)
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', args.real, '-t', str(dur),
            '-c:v', 'libx264', '-preset', 'fast',
            '-crf', str(args.crf)
        ]
        if args.bitrate:
            cmd += ['-b:v', args.bitrate]
        if not args.keep_audio:
            cmd += ['-an']
        else:
            cmd += ['-c:a', 'copy']
        cmd += [args.out_real]
        run_cmd(cmd)

    print(f"Trimmed & aligned videos saved as:\n  {args.out_real}\n  {args.out_gen}")

if __name__ == '__main__':
    main()
