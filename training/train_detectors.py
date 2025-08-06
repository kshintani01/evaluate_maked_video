# training/train_detectors.py

import pickle
import torch
from torch import nn, optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm

from detectors import XceptionPP, ViTDetector, MEAN, STD, DEVICE

def train_detector(detector_cls, input_size, epochs=5, batch_size=16):
    """ detector_cls（XceptionPP または ViTDetector）を input_size で学習 """
    print(f"=== Training {detector_cls.__name__} (input {input_size}×{input_size}) ===")

    # モデルと最適化器のセットアップ
    detector = detector_cls(pretrained=True)
    model = detector.model.to(DEVICE)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    # モデル固有の前処理
    transform = transforms.Compose([
        transforms.Resize(input_size),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    # データローダー
    dataset = datasets.ImageFolder(root="frames/aligned/", transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    # 学習ループ（tqdmでバッチごとの進捗表示）
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        progress_bar = tqdm(
            loader,
            desc=f"[{detector_cls.__name__}] Epoch {epoch}/{epochs}",
            unit="batch"
        )
        for imgs, labels in progress_bar:
            imgs   = imgs.to(DEVICE)
            labels = labels.float().unsqueeze(1).to(DEVICE)

            optimizer.zero_grad()
            logits = model(imgs)
            loss   = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * imgs.size(0)
            progress_bar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = running_loss / len(dataset)
        print(f"[{detector_cls.__name__}] Epoch {epoch}/{epochs} completed. Avg loss: {avg_loss:.4f}")

    # 学習済み重みをラッパーに反映して返す
    detector.model.load_state_dict(model.state_dict())
    return detector

if __name__ == '__main__':
    # XceptionPP を 299×299 で学習
    det_x = train_detector(XceptionPP, input_size=299, epochs=5)

    # ViTDetector を 224×224 で学習
    det_v = train_detector(ViTDetector, input_size=224, epochs=5)

    # 学習済検出器を保存
    with open('detectors.pkl', 'wb') as f:
        pickle.dump([det_x, det_v], f)
    print("ファインチューニング済みモデルを detectors.pkl に保存しました。")
