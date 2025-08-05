# detectors.py

import cv2
import torch
import timm
import torchvision.transforms as T
from PIL import Image

# ImageNet 標準の mean/std
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]

# 使用デバイス（CUDAがあればGPU、なければCPU）
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class XceptionPP:
    def __init__(self):
        # Xception を 1クラス出力に切り替え
        self.model = timm.create_model('xception', pretrained=True, num_classes=1)
        self.model.to(DEVICE).eval()
        self.transform = T.Compose([
            T.Resize(299),
            T.CenterCrop(299),
            T.ToTensor(),
            T.Normalize(MEAN, STD),
        ])

    def predict(self, img):
        """
        img: BGR numpy array (H, W, 3)
        戻り値: Fake と判断する確率（0〜1）
        """
        # BGR→RGB→PIL→Tensor
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x = self.transform(Image.fromarray(rgb)).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            logit = self.model(x)
            prob = torch.sigmoid(logit)[0].item()
        return prob

class ViTDetector:
    def __init__(self):
        self.model = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=1)
        self.model.to(DEVICE).eval()
        self.transform = T.Compose([
            T.Resize(224),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(MEAN, STD),
        ])

    def predict(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x = self.transform(Image.fromarray(rgb)).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            logit = self.model(x)
            prob = torch.sigmoid(logit)[0].item()
        return prob
