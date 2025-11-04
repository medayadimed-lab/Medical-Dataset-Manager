import os
from pathlib import Path
import numpy as np
from PIL import Image
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

ANON_FOLDER = "data/anonymized"
AUG_FOLDER = "data/augmented"
AUG_PARAMS = config["augmentation"]

def add_noise(image, noise_level=0.05):
    noise = np.random.randn(*image.shape) * 255 * noise_level
    noisy = image + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def augment_image(image_path):
    img = np.array(Image.open(image_path).convert("L"))
    images = [img]

    if AUG_PARAMS["flip"]:
        images.append(np.fliplr(img))
        images.append(np.flipud(img))
    for angle in AUG_PARAMS["rotate"]:
        images.append(np.array(Image.fromarray(img).rotate(angle)))
    images.append(add_noise(img, AUG_PARAMS["noise"]))
    return images

def augment_folder(folder_path=ANON_FOLDER):
    folder_path = Path(folder_path)
    AUG_FOLDER_PATH = Path(AUG_FOLDER)
    AUG_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

    for file in folder_path.glob("*.dcm"):
        augmented_imgs = augment_image(file)
        for idx, img in enumerate(augmented_imgs):
            out_name = f"{file.stem}_aug{idx}.png"
            out_path = AUG_FOLDER_PATH / out_name
            Image.fromarray(img).save(out_path)

    print(f"Augmentation complete. Files saved in {AUG_FOLDER_PATH}")
