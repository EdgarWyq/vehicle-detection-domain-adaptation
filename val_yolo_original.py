from vehicle_yolo.config import ORIGINAL_LOCAL_YAML, ORIGINAL_TRAIN_RUN_NAME
from vehicle_yolo.runner import validate_model
from vehicle_yolo.splits import create_original_sunny_night_split


def main() -> None:
    create_original_sunny_night_split()
    validate_model(
        data_yaml=ORIGINAL_LOCAL_YAML,
        run_name=ORIGINAL_TRAIN_RUN_NAME,
        val_name="val_original",
    )


if __name__ == "__main__":
    main()

