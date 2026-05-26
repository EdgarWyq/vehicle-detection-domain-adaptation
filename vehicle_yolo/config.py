from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "dataset" / "raw" / "ICDEC_challenge_2024-main"
LOCAL_YAML = PROJECT_ROOT / "local.yaml"
ORIGINAL_LOCAL_YAML = PROJECT_ROOT / "local_sunny_night_original.yaml"
SPLITS_DIR = PROJECT_ROOT / "splits"
ORIGINAL_TRAIN_LIST = SPLITS_DIR / "sunny_night_original_train.txt"
ORIGINAL_VAL_LIST = SPLITS_DIR / "sunny_night_original_val.txt"
RUNS_DIR = PROJECT_ROOT / "runs" / "detect"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
IGNORED_LABEL_FILES = {"classes.txt", "train.txt", "val.txt", "valid.txt", "test.txt"}

CLASS_NAMES = [
    "car",
    "bike",
    "auto",
    "rickshaw",
    "cycle",
    "bus",
    "minitruck",
    "truck",
    "van",
    "taxi",
    "motorvan",
    "toto",
    "train",
    "boat",
    "cycle van",
]
NUM_CLASSES = len(CLASS_NAMES)

CHECK_SPLITS = [
    (
        "Train/Sunny/Night",
        DATASET_ROOT / "images" / "Train" / "Sunny" / "Night",
        DATASET_ROOT / "labels" / "Train" / "Sunny" / "Night",
    ),
    (
        "Val/Sunny/Night",
        DATASET_ROOT / "images" / "Val" / "Sunny" / "Night",
        DATASET_ROOT / "labels" / "Val" / "Sunny" / "Night",
    ),
]

NEGATIVE_SUBDIR = Path("Sunny") / "Night" / "HardNegative"
NEGATIVE_SOURCE_ARCHIVE_DIR = PROJECT_ROOT / "dataset" / "hard_negative_sources" / "sunny_night"
NEGATIVE_SOURCE_SEARCH_DIRS = [
    Path.home() / "Desktop",
    NEGATIVE_SOURCE_ARCHIVE_DIR,
    Path.home() / "xwechat_files",
]
GENERATED_NEGATIVE_PREFIX = "hard_negative_sunny_night_"
NEGATIVE_COPIES_PER_IMAGE = 5
NEGATIVE_SAMPLE_FILES = [
    "8e44b162e247d3a0baaf636d22a522c7.jpg",
    "b43b4b9092f28b1605419ee711817112.jpg",
    "fc182126e152ddfd11e89db4488af0dc.jpg",
    "ea8189f1309d88d74536b31c6d38325e.jpg",
    "9c1bb6ac57628b037b10980dec98960c.jpg",
    "84a8cbbbd3e2299a8d10016845fef81f.jpg",
    "8fc7aac4630c0e5bacc102ce3e76d7ce.jpg",
    "2100f154626a417e58893a9655ecb2b1.jpg",
    "165a545cfcbe899703c996ec23b7c30c.jpg",
    "616e6a985dee4f3e8880d9796377d22c.jpg",
    "f462412c6ffb7906f96d6d47cef2c776.jpg",
    "426c44f787459e9c2b8f9953d41c5782.jpg",
]

MODEL_NAME = "yolo11s.pt"
TRAIN_RUN_NAME = "yolo11s_960_sunny_night_noaug_hardneg"
ORIGINAL_TRAIN_RUN_NAME = "yolo11s_960_sunny_night_noaug_original"
BEST_MODEL = RUNS_DIR / TRAIN_RUN_NAME / "weights" / "best.pt"
ORIGINAL_BEST_MODEL = RUNS_DIR / ORIGINAL_TRAIN_RUN_NAME / "weights" / "best.pt"

TRAIN_ARGS = {
    "epochs": 100,
    "imgsz": 960,
    "batch": 4,
    "device": 0,
    "workers": 4,
    "amp": True,
    "cache": False,
    "rect": True,
    "patience": 30,
    "seed": 42,
    "deterministic": True,
    "optimizer": "auto",
    "cos_lr": True,
    "hsv_h": 0.0,
    "hsv_s": 0.0,
    "hsv_v": 0.0,
    "degrees": 0.0,
    "translate": 0.0,
    "scale": 0.0,
    "shear": 0.0,
    "perspective": 0.0,
    "flipud": 0.0,
    "fliplr": 0.0,
    "bgr": 0.0,
    "mosaic": 0.0,
    "mixup": 0.0,
    "cutmix": 0.0,
    "copy_paste": 0.0,
    "erasing": 0.0,
}

VAL_ARGS = {
    "imgsz": 960,
    "batch": 4,
    "device": 0,
    "workers": 4,
    "rect": True,
}

PREDICT_ARGS = {
    "imgsz": 960,
    "conf": 0.25,
    "device": 0,
    "save": True,
    "exist_ok": True,
}

VAL_SCENES = [
    ("sunny_night", DATASET_ROOT / "images" / "Val" / "Sunny" / "Night"),
]


def negative_source_paths() -> List[Path]:
    return [NEGATIVE_SOURCE_ARCHIVE_DIR / file_name for file_name in NEGATIVE_SAMPLE_FILES]
