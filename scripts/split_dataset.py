import os
from pathlib import Path
import random
from shutil import copy2
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

AUG_FOLDER = "data/augmented"
SPLIT_FOLDER = "data/splits"
RATIOS = config["split_ratios"]
SEED = config["seed"]

def split_dataset(folder_path=AUG_FOLDER):
    random.seed(SEED)
    folder_path = Path(folder_path)
    SPLIT_FOLDER_PATH = Path(SPLIT_FOLDER)
    for split in RATIOS:
        (SPLIT_FOLDER_PATH / split).mkdir(parents=True, exist_ok=True)

    files = list(folder_path.glob("*.png"))
    random.shuffle(files)

    n = len(files)
    train_end = int(n * RATIOS["train"])
    val_end = train_end + int(n * RATIOS["val"])

    for f in files[:train_end]:
        copy2(f, SPLIT_FOLDER_PATH / "train")
    for f in files[train_end:val_end]:
        copy2(f, SPLIT_FOLDER_PATH / "val")
    for f in files[val_end:]:
        copy2(f, SPLIT_FOLDER_PATH / "test")

    print(f"Dataset split complete. Check {SPLIT_FOLDER_PATH}")
