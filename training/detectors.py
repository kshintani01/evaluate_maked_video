# detectors.py

import cv2
import torch
import timm
import torchvision.transforms as T
from PIL import Image

#――――――――――――――――――――――――――
# 前処理／デバイス設定用定数
#――――――――――――――――――――――――――
# ImageNet 標準の mean/std
MEAN = [0.485, 0.456, 0.406]
STD  = [0.229, 0.224, 0.225]

# 使用デバイス（CUDAがあれば GPU、なければ CPU）
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#――――――――――――――――――――――――――
# ベースクラス（Optional）
#――――――――――――――――――――――――――
class BaseDetector:
    def __init__(self, model_name: str, input_size: int, num_classes: int = 1,
                 pretrained: bool = True, weight_path: str = None):
        # モデル生成
        self.model = timm.create_model(
            model_name,
            pretrained=pretrained,
            num_classes=num_classes
        ).to(DEVICE).eval()

        # カスタム重みがあればロード
        if weight_path is not None:
            state_dict = torch.load(weight_path, map_location=DEVICE)
            self.model.load_state_dict(state_dict)

        # 前処理パイプライン
        self.transform = T.Compose([
            T.Resize(input_size),
            T.CenterCrop(input_size),
            T.ToTensor(),
            T.Normalize(MEAN, STD),
        ])

    def predict(self, img):
        """
        img: BGR numpy array (H, W, 3)
        return: Fake と判断する確率（0〜1）
        """
        # BGR→RGB→PIL→Tensor
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x = self.transform(Image.fromarray(rgb)) \
                .unsqueeze(0) \
                .to(DEVICE)

        with torch.no_grad():
            logit = self.model(x)
            prob  = torch.sigmoid(logit)[0].item()
        return prob

#――――――――――――――――――――――――――
# 各種検出器クラス
#――――――――――――――――――――――――――
class XceptionPP(BaseDetector):
    def __init__(self, pretrained: bool = True, weight_path: str = None):
        super().__init__(
            model_name='xception',
            input_size=299,
            num_classes=1,
            pretrained=pretrained,
            weight_path=weight_path
        )

class ViTDetector(BaseDetector):
    def __init__(self, pretrained: bool = True, weight_path: str = None):
        super().__init__(
            model_name='vit_base_patch16_224',
            input_size=224,
            num_classes=1,
            pretrained=pretrained,
            weight_path=weight_path
        )

#――――――――――――――――――――――――――
# モジュールエクスポート指定
#――――――――――――――――――――――――――
__all__ = [
    'XceptionPP', 'ViTDetector',
    'MEAN', 'STD', 'DEVICE'
]
