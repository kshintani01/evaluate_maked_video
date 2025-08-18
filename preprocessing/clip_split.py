import cv2, os
import numpy as np

def split_clips(src_dir, dst_dir, clip_size=16):
    os.makedirs(dst_dir, exist_ok=True)
    imgs = sorted(os.listdir(src_dir))
    for i in range(0, len(imgs)-clip_size+1):
        clip = []
        for j in range(clip_size):
            clip.append(cv2.imread(f"{src_dir}/{imgs[i+j]}"))
        # 例：clip_0001.npz で保存
        np.savez(f"{dst_dir}/clip_{i:04d}.npz", frames=clip)

split_clips("frames/aligned/real", "clips/real", clip_size=16)
split_clips("frames/aligned/gen",  "clips/gen",  clip_size=16)
