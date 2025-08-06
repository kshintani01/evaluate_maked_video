#!/usr/bin/env python3
# compute_fvd.py

import glob
import numpy as np
import scipy.linalg as la
import torch
import torch.nn.functional as F
from pytorchvideo.models.hub import i3d_r50

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

def frechet_distance(mu1, sigma1, mu2, sigma2, eps=1e-6):
    """
    Fréchet 距離を安定的に計算（共分散に eps·I を足してから sqrtm）
    """
    diff = mu1 - mu2
    # eps·I を足して数値安定化
    dim = sigma1.shape[0]
    offset = eps * np.eye(dim)
    cov_prod = (sigma1 + offset).dot(sigma2 + offset)
    covmean, _ = la.sqrtm(cov_prod, disp=False)
    covmean = np.real_if_close(covmean, tol=1e-5)
    return diff.dot(diff) + np.trace(sigma1 + sigma2 - 2 * covmean)

def extract_feats(clip_path, model, device):
    """
    ・リサイズ／センタークロップ／正規化を追加
    ・分類ヘッドを除いたブロックで特徴抽出
    """
    data = np.load(clip_path)['frames']  # (T, H, W, C)
    x = torch.from_numpy(data).permute(3,0,1,2).unsqueeze(0).float()  # (1, C, T, H, W)

    # --- 前処理 (PyTorchVideo デフォルト) ---
    # 短辺を256にスケール → 224×224でセンタークロップ
    _, C, T, H, W = x.shape
    if H < W:
        new_h, new_w = 256, int(W * 256 / H)
    else:
        new_h, new_w = int(H * 256 / W), 256
    x = F.interpolate(x, size=(T, new_h, new_w), mode='trilinear', align_corners=False)

    h_off = (new_h - 224) // 2
    w_off = (new_w - 224) // 2
    x = x[:,:,:, h_off:h_off+224, w_off:w_off+224]

    # チャンネル正規化：video_mean=(0.45,0.45,0.45), video_std=(0.225,0.225,0.225) :contentReference[oaicite:0]{index=0}
    mean = torch.tensor([0.45, 0.45, 0.45]).view(1,3,1,1,1)
    std  = torch.tensor([0.225,0.225,0.225]).view(1,3,1,1,1)
    x = (x / 255.0 - mean) / std

    x = x.to(device)

    # --- 分類ヘッド直前のプーリング特徴を抽出（blocks[:-1]） :contentReference[oaicite:1]{index=1} ---
    with torch.no_grad():
        f = x
        for blk in model.blocks[:-1]:
            f = blk(f)
        # 時間＋空間 次元で平均プール → (1, 2048)
        f = f.mean(dim=[2,3,4])

    return f.cpu().numpy().reshape(-1)

def main():
    print("[FVD] Loading I3D model...")
    model = i3d_r50(pretrained=True).eval().to(DEVICE)

    # 実動画・生成動画クリップのパス収集
    real_paths = sorted(glob.glob("clips/real/*.npz"))
    gen_paths  = sorted(glob.glob("clips/gen/*.npz"))

    # 特徴抽出
    print(f"[FVD] Extracting features: real={len(real_paths)}, gen={len(gen_paths)}")
    # real clips
    r_feats = []
    for idx, p in enumerate(real_paths, start=1):
        print(f"[FVD] Real clip {idx}/{len(real_paths)}", end='\r', flush=True)
        r_feats.append(extract_feats(p, model, DEVICE))
    print()  # 改行
    # gen clips
    g_feats = []
    for idx, p in enumerate(gen_paths, start=1):
        print(f"[FVD] Gen clip  {idx}/{len(gen_paths)}", end='\r', flush=True)
        g_feats.append(extract_feats(p, model, DEVICE))
    print()  # 改行

    # 統計量計算
    r_feats = np.stack(r_feats)
    g_feats = np.stack(g_feats)
    mu_r = r_feats.mean(axis=0)
    mu_g = g_feats.mean(axis=0)
    sigma_r = np.cov(r_feats, rowvar=False)
    sigma_g = np.cov(g_feats, rowvar=False)

    # FVD 計算
    print("[FVD] Computing Fréchet Video Distance...")
    fvd_value = frechet_distance(mu_r, sigma_r, mu_g, sigma_g)
    print(f"[FVD] FVD: {fvd_value:.2f}")

if __name__ == '__main__':
    main()
