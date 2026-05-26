from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Dict, List, Tuple

from .config import (
    CHECK_SPLITS,
    DATASET_ROOT,
    GENERATED_NEGATIVE_PREFIX,
    IGNORED_LABEL_FILES,
    IMAGE_EXTENSIONS,
    NEGATIVE_COPIES_PER_IMAGE,
    NEGATIVE_SAMPLE_FILES,
    NEGATIVE_SUBDIR,
    NEGATIVE_SOURCE_ARCHIVE_DIR,
    NEGATIVE_SOURCE_SEARCH_DIRS,
    NUM_CLASSES,
)


MAX_ERRORS_TO_SHOW = 30


@dataclass
class SplitReport:
    split_name: str
    image_count: int
    label_count: int
    empty_label_count: int
    missing_label_count: int
    extra_label_count: int
    format_error_count: int
    class_counts: Dict[int, int]
    errors: List[str]


def find_images(folder: Path) -> List[Path]:
    return sorted(
        path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def find_labels(folder: Path) -> List[Path]:
    return sorted(
        path
        for path in folder.rglob("*.txt")
        if path.is_file() and path.name.lower() not in IGNORED_LABEL_FILES
    )


def check_label_file(label_path: Path) -> Tuple[List[str], Dict[int, int]]:
    errors = []
    class_counts = {class_id: 0 for class_id in range(NUM_CLASSES)}

    try:
        lines = label_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = label_path.read_text(encoding="gbk").splitlines()

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) != 5:
            errors.append(f"{label_path} line {line_number}: expected 5 values, got {len(parts)}")
            continue

        class_text, *box_text = parts
        if not class_text.isdigit():
            errors.append(f"{label_path} line {line_number}: class id is not an integer")
            continue

        class_id = int(class_text)
        if class_id < 0 or class_id >= NUM_CLASSES:
            errors.append(f"{label_path} line {line_number}: class id {class_id} is outside 0-{NUM_CLASSES - 1}")
            continue

        try:
            x_center, y_center, width, height = [float(value) for value in box_text]
        except ValueError:
            errors.append(f"{label_path} line {line_number}: box values must be numbers")
            continue

        values = [x_center, y_center, width, height]
        if any(value < 0 or value > 1 for value in values):
            errors.append(f"{label_path} line {line_number}: box values must be between 0 and 1")
            continue

        if width <= 0 or height <= 0:
            errors.append(f"{label_path} line {line_number}: width and height must be greater than 0")
            continue

        class_counts[class_id] += 1

    return errors, class_counts


def check_split(split_name: str, image_dir: Path, label_dir: Path) -> SplitReport:
    if not image_dir.exists():
        return SplitReport(split_name, 0, 0, 0, 0, 0, 0, {}, [f"Missing image folder: {image_dir}"])
    if not label_dir.exists():
        return SplitReport(split_name, 0, 0, 0, 0, 0, 0, {}, [f"Missing label folder: {label_dir}"])

    images = find_images(image_dir)
    labels = find_labels(label_dir)

    image_keys = {image.relative_to(image_dir).with_suffix("") for image in images}
    label_keys = {label.relative_to(label_dir).with_suffix("") for label in labels}

    missing_labels = sorted(image_keys - label_keys)
    extra_labels = sorted(label_keys - image_keys)
    errors = []

    for relative_path in missing_labels:
        errors.append(f"{split_name}: missing label for image {relative_path}")
    for relative_path in extra_labels:
        errors.append(f"{split_name}: label has no matching image {relative_path}")

    format_errors = []
    split_class_counts = {class_id: 0 for class_id in range(NUM_CLASSES)}
    for label_path in labels:
        label_errors, label_class_counts = check_label_file(label_path)
        format_errors.extend(label_errors)
        for class_id, count in label_class_counts.items():
            split_class_counts[class_id] += count

    errors.extend(format_errors)
    empty_label_count = sum(1 for label in labels if label.stat().st_size == 0)

    return SplitReport(
        split_name=split_name,
        image_count=len(images),
        label_count=len(labels),
        empty_label_count=empty_label_count,
        missing_label_count=len(missing_labels),
        extra_label_count=len(extra_labels),
        format_error_count=len(format_errors),
        class_counts=split_class_counts,
        errors=errors,
    )


def print_report(report: SplitReport) -> None:
    print(f"\n[{report.split_name}]")
    print(f"Images: {report.image_count}")
    print(f"Labels: {report.label_count}")
    print(f"Empty labels: {report.empty_label_count}")
    print(f"Missing labels: {report.missing_label_count}")
    print(f"Extra labels: {report.extra_label_count}")
    print(f"Format errors: {report.format_error_count}")
    print("Objects per class:")
    for class_id, count in report.class_counts.items():
        print(f"  class {class_id}: {count}")


def check_dataset(exit_on_error: bool = True) -> List[SplitReport]:
    print(f"Dataset root: {DATASET_ROOT}")
    print(f"Number of classes: {NUM_CLASSES}")

    reports = [check_split(split_name, image_dir, label_dir) for split_name, image_dir, label_dir in CHECK_SPLITS]
    all_errors = []
    for report in reports:
        print_report(report)
        all_errors.extend(report.errors)

    print("\n[Summary]")
    if not all_errors:
        print("Dataset check passed.")
        return reports

    print(f"Found {len(all_errors)} problem(s). Showing first {MAX_ERRORS_TO_SHOW}:")
    for error in all_errors[:MAX_ERRORS_TO_SHOW]:
        print(f"- {error}")
    if len(all_errors) > MAX_ERRORS_TO_SHOW:
        print(f"... and {len(all_errors) - MAX_ERRORS_TO_SHOW} more.")

    if exit_on_error:
        raise SystemExit(1)
    return reports


def remove_generated_negative_samples() -> None:
    for split_name in ["Train", "Val"]:
        for root_name in ["images", "labels"]:
            folder = DATASET_ROOT / root_name / split_name / NEGATIVE_SUBDIR
            if not folder.exists():
                continue

            for path in folder.glob(f"{GENERATED_NEGATIVE_PREFIX}*"):
                if path.is_file():
                    path.unlink()

            try:
                folder.rmdir()
            except OSError:
                pass


def find_negative_source(file_name: str) -> Path:
    for search_dir in NEGATIVE_SOURCE_SEARCH_DIRS:
        candidate = search_dir / file_name
        if candidate.exists():
            return candidate

    for search_dir in NEGATIVE_SOURCE_SEARCH_DIRS:
        if not search_dir.exists():
            continue

        matches = sorted(search_dir.rglob(file_name))
        if matches:
            return matches[0]

    raise FileNotFoundError(file_name)


def archive_negative_sources() -> Tuple[List[Path], List[str]]:
    source_paths = []
    missing = []
    NEGATIVE_SOURCE_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for file_name in NEGATIVE_SAMPLE_FILES:
        try:
            source_path = find_negative_source(file_name)
        except FileNotFoundError:
            missing.append(file_name)
            continue

        archive_path = NEGATIVE_SOURCE_ARCHIVE_DIR / file_name
        if source_path.resolve() != archive_path.resolve():
            shutil.copy2(str(source_path), str(archive_path))
        source_paths.append(archive_path)

    return source_paths, missing


def copy_negative_samples() -> None:
    source_paths, missing = archive_negative_sources()
    if missing:
        print("\nMissing source images:")
        for file_name in missing:
            print(f"- {file_name}")
        print(f"\nPlace the images above in: {NEGATIVE_SOURCE_ARCHIVE_DIR}")
        raise SystemExit(1)

    copied = 0
    remove_generated_negative_samples()

    for source_index, source_path in enumerate(source_paths, start=1):
        image_dir = DATASET_ROOT / "images" / "Train" / NEGATIVE_SUBDIR
        label_dir = DATASET_ROOT / "labels" / "Train" / NEGATIVE_SUBDIR
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

        for copy_index in range(1, NEGATIVE_COPIES_PER_IMAGE + 1):
            destination_stem = (
                f"{GENERATED_NEGATIVE_PREFIX}"
                f"src{source_index:02d}_copy{copy_index:02d}_{source_path.stem}"
            )
            destination_image = image_dir / f"{destination_stem}{source_path.suffix.lower()}"
            destination_label = label_dir / f"{destination_stem}.txt"

            shutil.copy2(str(source_path), str(destination_image))
            destination_label.write_text("", encoding="utf-8")
            copied += 1

            print(f"Train: {destination_image.relative_to(DATASET_ROOT)}")

    print(
        f"\nCopied {copied} hard negative image(s) with empty YOLO labels "
        f"({len(source_paths)} source image(s) x {NEGATIVE_COPIES_PER_IMAGE} copies)."
    )
