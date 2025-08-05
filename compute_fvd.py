#!/usr/bin/env python3
# compute_fvd.py

import os
import glob
import numpy as np
import scipy.linalg as la
import torch
from pytorchvideo.models.hub import i3d_r50

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


def frechet_distance(mu1, s1, mu2, s2):
    diff = mu1 - mu2
    covmean = la.sqrtm(s1.dot(s2))
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    return diff.dot(diff) + np.trace(s1 + s2 - 2*covmean)


def extract_feats(clip_path, model):
    data = np.load(clip_path)['frames']  # (T,H,W,C)
    x = torch.from_numpy(data).permute(3,0,1,2).unsqueeze(0).float().to(DEVICE)
    with torch.no_grad():
        f = x
        for blk in model.blocks:
            f = blk(f)
        f = f.mean(dim=list(range(2, f.ndim)), keepdim=True).squeeze()
    return f.cpu().numpy().reshape(-1)


def main():
    # モデルロード
    print("[FVD] Loading I3D model...")
    model = i3d_r50(pretrained=True).eval().to(DEVICE)
    # Real clips
    real_paths = sorted(glob.glob("clips/real/*.npz"))
    total_r = len(real_paths)
    r_feats = []
    print(f"[FVD] Extracting features from real clips: {total_r} clips")
    for idx, path in enumerate(real_paths, start=1):
        print(f"[FVD] Real clip {idx}/{total_r}", end='\r', flush=True)
        feat = extract_feats(path, model)
        r_feats.append(feat)
    print()  # newline after progress

    # Gen clips
    gen_paths = sorted(glob.glob("clips/gen/*.npz"))
    total_g = len(gen_paths)
    g_feats = []
    print(f"[FVD] Extracting features from generated clips: {total_g} clips")
    for idx, path in enumerate(gen_paths, start=1):
        print(f"[FVD] Gen clip  {idx}/{total_g}", end='\r', flush=True)
        feat = extract_feats(path, model)
        g_feats.append(feat)
    print()

    # スタッキング
    r_feats = np.stack(r_feats)
    g_feats = np.stack(g_feats)

    # 分布のμ, Σ計算
    print("[FVD] Computing mean and covariance...")
    mu_r = r_feats.mean(axis=0)
    mu_g = g_feats.mean(axis=0)
    sigma_r = np.cov(r_feats, rowvar=False)
    sigma_g = np.cov(g_feats, rowvar=False)

    # Fréchet距離計算
    print("[FVD] Computing Fréchet Video Distance...")
    fvd_value = frechet_distance(mu_r, sigma_r, mu_g, sigma_g)
    print(f"[FVD] FVD: {fvd_value:.2f}")

if __name__ == '__main__':
    main()
