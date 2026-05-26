from vehicle_yolo.config import ORIGINAL_LOCAL_YAML, ORIGINAL_TRAIN_RUN_NAME
from vehicle_yolo.runner import train_model
from vehicle_yolo.splits import create_original_sunny_night_split


def main() -> None:
    create_original_sunny_night_split()
    train_model(data_yaml=ORIGINAL_LOCAL_YAML, run_name=ORIGINAL_TRAIN_RUN_NAME)


if __name__ == "__main__":
    main()

