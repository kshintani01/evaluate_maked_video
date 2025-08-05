# generate_detectors.py
import pickle
from detectors import XceptionPP, ViTDetector

def main():
    det1 = XceptionPP()
    det2 = ViTDetector()
    with open('detectors.pkl', 'wb') as f:
        pickle.dump([det1, det2], f)
    print("detectors.pkl を作成しました。")

if __name__ == '__main__':
    main()
