#!/usr/bin/env python3
# extract_sequence_features.py

import os
import argparse
import numpy as np
import cv2
import mediapipe as mp

mp_face = mp.solutions.face_mesh

def compute_sequence(aligned_dir):
    seq = []
    face = mp_face.FaceMesh(static_image_mode=True)
    for fn in sorted(os.listdir(aligned_dir)):
        img = cv2.imread(os.path.join(aligned_dir, fn))
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = face.process(rgb)
        if not res.multi_face_landmarks:
            seq.append([0.0, 0.0])
            continue
        lm = res.multi_face_landmarks[0].landmark
        pts = np.array([[p.x * img.shape[1], p.y * img.shape[0]] for p in lm])
        # 口開度: 上唇13 – 下唇14
        mouth = np.linalg.norm(pts[13] - pts[14])
        # 目開度: 左目上159 – 左目下386
        eye   = np.linalg.norm(pts[159] - pts[386])
        seq.append([mouth, eye])
    face.close()
    return np.array(seq)  # shape: (N_frames, 2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--aligned_real", required=True,
                   help="アライン済フレーム実写フォルダ")
    p.add_argument("--aligned_gen",  required=True,
                   help="アライン済フレーム生成フォルダ")
    p.add_argument("--out_dir",      required=True,
                   help="出力ディレクトリ (例: features)")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    real_seq = compute_sequence(args.aligned_real)
    gen_seq  = compute_sequence(args.aligned_gen)
    np.save(os.path.join(args.out_dir, "real.npy"), real_seq)
    np.save(os.path.join(args.out_dir, "gen.npy"),  gen_seq)
    print(f"Saved real sequence to {args.out_dir}/real.npy")
    print(f"Saved gen  sequence to {args.out_dir}/gen.npy")

if __name__ == "__main__":
    main()
