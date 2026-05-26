from typing import List

from vehicle_yolo.config import (
    ORIGINAL_TRAIN_RUN_NAME,
    ORIGINAL_VAL_LIST,
    PREDICT_ARGS,
    RUNS_DIR,
    TRAIN_RUN_NAME,
)
from vehicle_yolo.runner import best_model_for_run


PREDICT_RUNS = [
    ("hardneg", TRAIN_RUN_NAME),
    ("original", ORIGINAL_TRAIN_RUN_NAME),
]


def load_val_images() -> List[str]:
    if not ORIGINAL_VAL_LIST.exists():
        raise FileNotFoundError(f"Missing validation list: {ORIGINAL_VAL_LIST}")
    return [line.strip() for line in ORIGINAL_VAL_LIST.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    from ultralytics import YOLO

    image_paths = load_val_images()
    print(f"Validation images: {len(image_paths)}")

    for short_name, run_name in PREDICT_RUNS:
        model_path = best_model_for_run(run_name)
        if not model_path.exists():
            raise FileNotFoundError(f"Missing model: {model_path}")

        output_name = f"predict_sunny_night_{short_name}"
        model = YOLO(str(model_path))

        print(f"\nPredicting {short_name}: {model_path}")
        model.predict(
            source=image_paths,
            project=str(RUNS_DIR),
            name=output_name,
            save_txt=True,
            save_conf=True,
            **PREDICT_ARGS,
        )
        print(f"Saved visualizations: {RUNS_DIR / output_name}")


if __name__ == "__main__":
    main()
