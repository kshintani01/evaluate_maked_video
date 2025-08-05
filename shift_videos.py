#!/usr/bin/env python3
# shift_videos_trim.py

import argparse
import subprocess
import sys

"""
Trim (frame-shift) real or generated videos based on detected optimal shift.
Positive shift: drop initial frames from real video.
Negative shift: drop initial frames from generated video.
Re-encodes trimmed video.

Usage:
    python shift_videos_trim.py \
      --real       real.mp4 \
      --gen        gen.mp4 \
      --shift      16 \
      --fps        30 \
      --out_real   real_shifted.mp4 \
      --out_gen    gen_shifted.mp4
"""

def trim_video(input_path, output_path, frame_trim, fps):
    seconds = frame_trim / fps
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-ss', str(seconds), '-i', input_path,
        '-c:v', 'libx264', '-preset', 'fast',
        '-c:a', 'copy', output_path
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ffmpeg trimming failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Trim videos by frame offset")
    parser.add_argument('--real',     required=True, help='Path to real video')
    parser.add_argument('--gen',      required=True, help='Path to generated video')
    parser.add_argument('--shift',    type=int, required=True,
                        help='Frame shift: positive to trim from real, negative from gen')
    parser.add_argument('--fps',      type=int, default=30, help='Frame rate')
    parser.add_argument('--out_real', required=True, help='Output path for real')
    parser.add_argument('--out_gen',  required=True, help='Output path for gen')
    args = parser.parse_args()

    if args.shift >= 0:
        print(f"Trimming {args.shift} frames from real video...")
        trim_video(args.real, args.out_real, args.shift, args.fps)
        # Copy gen unchanged
        subprocess.run(['cp', args.gen, args.out_gen], check=True)
    else:
        trim = -args.shift
        print(f"Trimming {trim} frames from generated video...")
        trim_video(args.gen, args.out_gen, trim, args.fps)
        subprocess.run(['cp', args.real, args.out_real], check=True)

    print(f"Trimmed videos saved as: {args.out_real}, {args.out_gen}")

if __name__ == '__main__':
    main()
