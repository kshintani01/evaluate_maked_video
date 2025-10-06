import cv2, os
import numpy as np

def split_clips(src_dir, dst_dir, clip_size=16):
    os.makedirs(dst_dir, exist_ok=True)
    
    # 画像ファイルのみをフィルタリング
    all_files = os.listdir(src_dir)
    imgs = sorted([f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    print(f"Processing {len(imgs)} images from {src_dir}")
    
    clip_count = 0
    for i in range(0, len(imgs)-clip_size+1):
        clip = []
        valid_clip = True
        
        for j in range(clip_size):
            img_path = f"{src_dir}/{imgs[i+j]}"
            img = cv2.imread(img_path)
            
            # 画像が正常に読み込めない場合のエラーハンドリング
            if img is None:
                print(f"Warning: Could not read image {img_path}")
                valid_clip = False
                break
            
            clip.append(img)
        
        # 全ての画像が有効な場合のみクリップを保存
        if valid_clip and len(clip) == clip_size:
            try:
                # numpyアレイに変換してから保存
                clip_array = np.stack(clip)
                np.savez(f"{dst_dir}/clip_{clip_count:04d}.npz", frames=clip_array)
                clip_count += 1
            except Exception as e:
                print(f"Error saving clip {clip_count}: {e}")
    
    print(f"Saved {clip_count} clips to {dst_dir}")

split_clips("frames/aligned/real", "clips/real", clip_size=16)
split_clips("frames/aligned/gen",  "clips/gen",  clip_size=16)
