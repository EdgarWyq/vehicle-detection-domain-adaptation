from pathlib import Path
from typing import List

from .config import (
    CLASS_NAMES,
    DATASET_ROOT,
    IMAGE_EXTENSIONS,
    ORIGINAL_LOCAL_YAML,
    ORIGINAL_TRAIN_LIST,
    ORIGINAL_VAL_LIST,
)


def _is_hard_negative(path: Path) -> bool:
    return any(part.lower() == "hardnegative" for part in path.parts)


def _find_original_images(image_dir: Path) -> List[Path]:
    return sorted(
        path
        for path in image_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and not _is_hard_negative(path)
    )


def _label_for_image(image_path: Path) -> Path:
    relative_image = image_path.relative_to(DATASET_ROOT / "images")
    return DATASET_ROOT / "labels" / relative_image.with_suffix(".txt")


def _write_image_list(output_path: Path, image_paths: List[Path]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [path.as_posix() for path in image_paths]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_original_yaml() -> None:
    lines = [
        f"path: {DATASET_ROOT.as_posix()}",
        f"train: {ORIGINAL_TRAIN_LIST.as_posix()}",
        f"val: {ORIGINAL_VAL_LIST.as_posix()}",
        "",
        f"nc: {len(CLASS_NAMES)}",
        "names:",
    ]
    lines.extend(f"  - {name}" for name in CLASS_NAMES)
    ORIGINAL_LOCAL_YAML.write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_original_sunny_night_split() -> None:
    train_dir = DATASET_ROOT / "images" / "Train" / "Sunny" / "Night"
    val_dir = DATASET_ROOT / "images" / "Val" / "Sunny" / "Night"

    train_images = _find_original_images(train_dir)
    val_images = _find_original_images(val_dir)

    missing_labels = []
    for image_path in train_images + val_images:
        label_path = _label_for_image(image_path)
        if not label_path.exists():
            missing_labels.append(str(label_path))

    if missing_labels:
        print("Missing labels:")
        for label_path in missing_labels[:30]:
            print(f"- {label_path}")
        if len(missing_labels) > 30:
            print(f"... and {len(missing_labels) - 30} more.")
        raise SystemExit(1)

    _write_image_list(ORIGINAL_TRAIN_LIST, train_images)
    _write_image_list(ORIGINAL_VAL_LIST, val_images)
    _write_original_yaml()

    print(f"Original train images: {len(train_images)} -> {ORIGINAL_TRAIN_LIST}")
    print(f"Original val images: {len(val_images)} -> {ORIGINAL_VAL_LIST}")
    print(f"Original data yaml: {ORIGINAL_LOCAL_YAML}")

