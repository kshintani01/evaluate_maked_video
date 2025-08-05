#!/usr/bin/env python3
# preprocess.py

import os, sys, argparse, subprocess, tempfile
import cv2, numpy as np
import mediapipe as mp
from scipy.signal import correlate

# 出力ディレクトリ
RAW_REAL = "frames/raw/real"
RAW_GEN  = "frames/raw/gen"
ALN_REAL = "frames/aligned/real"
ALN_GEN  = "frames/aligned/gen"
CLIPS_REAL = "clips/real"
CLIPS_GEN  = "clips/gen"

mp_face = mp.solutions.face_mesh

def load_and_resample(path, fps=30, width=720):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened(): sys.exit(f"ERROR: cannot open {path}")
    h = int(width * cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    tmp = os.path.join(tempfile.gettempdir(), f"rs_{os.path.basename(path)}")
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width,h))
    while True:
        ret, img = cap.read()
        if not ret: break
        vw.write(cv2.resize(img,(width,h)))
    cap.release(); vw.release()
    return tmp

def extract_frames(video, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cmd = ['ffmpeg','-hide_banner','-loglevel','error','-i',
           video, os.path.join(out_dir,'%05d.png')]
    subprocess.run(cmd, check=True)

def detect_align(in_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    face = mp_face.FaceMesh(static_image_mode=True)
    for fn in sorted(os.listdir(in_dir)):
        img = cv2.imread(os.path.join(in_dir,fn))
        rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        res = face.process(rgb)
        if not res.multi_face_landmarks: continue
        lm = res.multi_face_landmarks[0].landmark
        h,w = img.shape[:2]
        pts = np.float32([[p.x*w,p.y*h] for p in lm])
        src = pts[[33,263,1]]  # 左目外、右目外、鼻根
        dst = np.float32([[80,80],[176,80],[128,176]])
        M = cv2.getAffineTransform(src,dst)
        out = cv2.warpAffine(img,M,(256,256))
        cv2.imwrite(os.path.join(out_dir,fn),out)
    face.close()

def make_clips(aln_dir, clip_dir, size=16):
    os.makedirs(clip_dir, exist_ok=True)
    files = sorted(os.listdir(aln_dir))
    for i in range(len(files)-size+1):
        clip = [cv2.imread(os.path.join(aln_dir,files[i+j])) for j in range(size)]
        np.savez(os.path.join(clip_dir,f"clip_{i:04d}.npz"),frames=np.stack(clip))

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--real', required=True)
    p.add_argument('--gen',  required=True)
    args = p.parse_args()

    # STEP 1: リサンプル＋抽出
    r_rs = load_and_resample(args.real); g_rs = load_and_resample(args.gen)
    extract_frames(r_rs, RAW_REAL); extract_frames(g_rs, RAW_GEN)

    # STEP 2: 空間アライン
    detect_align(RAW_REAL, ALN_REAL)
    detect_align(RAW_GEN,  ALN_GEN)

    # STEP 3: クリップ生成 (FVD用)
    make_clips(ALN_REAL, CLIPS_REAL)
    make_clips(ALN_GEN,  CLIPS_GEN)

    print("Preprocessing done.")

if __name__=='__main__':
    main()
