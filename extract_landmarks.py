#!/usr/bin/env python3
# extract_landmarks.py

import os
import argparse
import numpy as np
import cv2
import mediapipe as mp

mp_face = mp.solutions.face_mesh

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--aligned_dir', required=True,
                   help='frames/aligned/real などアライン済PNGが入ったフォルダ')
    p.add_argument('--out_npy', required=True,
                   help='出力ファイル例: landmarks/real.npy')
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out_npy), exist_ok=True)
    face = mp_face.FaceMesh(static_image_mode=True)
    landmarks = []

    for fn in sorted(os.listdir(args.aligned_dir)):
        img = cv2.imread(os.path.join(args.aligned_dir, fn))
        if img is None:
            landmarks.append(None)
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = face.process(rgb)
        if not res.multi_face_landmarks:
            landmarks.append(None)
        else:
            lm = res.multi_face_landmarks[0].landmark
            h, w = img.shape[:2]
            pts = np.array([[p.x*w, p.y*h] for p in lm], dtype=np.float32)
            landmarks.append(pts)

    face.close()
    # dtype=object で None も保存できるように
    np.save(args.out_npy, np.array(landmarks, dtype=object))
    print(f"Saved landmarks array to {args.out_npy}")

if __name__ == '__main__':
    main()
