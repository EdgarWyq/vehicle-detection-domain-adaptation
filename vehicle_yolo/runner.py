from pathlib import Path
from typing import List, Optional

from .config import (
    BEST_MODEL,
    LOCAL_YAML,
    MODEL_NAME,
    PREDICT_ARGS,
    RUNS_DIR,
    TRAIN_ARGS,
    TRAIN_RUN_NAME,
    VAL_ARGS,
    VAL_SCENES,
)
from .dataset import find_images


def _load_yolo():
    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Cannot import ultralytics. Install it with: "
            ".\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt"
        ) from exc
    return YOLO


def best_model_for_run(run_name: str) -> Path:
    return RUNS_DIR / run_name / "weights" / "best.pt"


def resolve_best_model(model_path: Optional[Path] = None, run_name: str = TRAIN_RUN_NAME) -> Path:
    if model_path is not None and model_path.exists():
        return model_path
    default_model = BEST_MODEL if run_name == TRAIN_RUN_NAME else best_model_for_run(run_name)
    if default_model.exists():
        return default_model

    raise FileNotFoundError(
        f"Cannot find best.pt at {default_model}. Run the matching train script first, or set your own model path."
    )


def train_model(
    data_yaml: Path = LOCAL_YAML,
    run_name: str = TRAIN_RUN_NAME,
    model_name: str = MODEL_NAME,
) -> None:
    YOLO = _load_yolo()
    model = YOLO(model_name)

    model.train(
        data=str(data_yaml),
        project=str(RUNS_DIR),
        name=run_name,
        exist_ok=True,
        **TRAIN_ARGS,
    )

    print(f"Training results saved in: {RUNS_DIR / run_name}")


def validate_model(
    model_path: Optional[Path] = None,
    data_yaml: Path = LOCAL_YAML,
    run_name: str = TRAIN_RUN_NAME,
    val_name: str = "val_best",
) -> None:
    YOLO = _load_yolo()
    best_model = resolve_best_model(model_path, run_name=run_name)
    model = YOLO(str(best_model))

    model.val(
        data=str(data_yaml),
        project=str(RUNS_DIR),
        name=val_name,
        exist_ok=True,
        **VAL_ARGS,
    )

    print(f"Validated model: {best_model}")
    print(f"Validation results saved in: {RUNS_DIR / val_name}")


def _image_paths_for_scene(source_dir: Path) -> List[str]:
    images = find_images(source_dir)
    if not images:
        raise FileNotFoundError(f"No images found in: {source_dir}")
    return [str(path) for path in images]


def predict_validation_scenes(model_path: Optional[Path] = None) -> None:
    YOLO = _load_yolo()
    best_model = resolve_best_model(model_path)
    model = YOLO(str(best_model))

    for scene_name, source_dir in VAL_SCENES:
        image_paths = _image_paths_for_scene(source_dir)
        run_name = f"predict_{scene_name}_{TRAIN_RUN_NAME}"

        print(f"Predicting {scene_name}: {len(image_paths)} image(s)")
        model.predict(
            source=image_paths,
            project=str(RUNS_DIR),
            name=run_name,
            **PREDICT_ARGS,
        )
        print(f"Prediction images saved in: {RUNS_DIR / run_name}")
