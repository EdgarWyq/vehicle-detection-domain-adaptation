from vehicle_yolo.dataset import check_dataset, copy_negative_samples


def main() -> None:
    copy_negative_samples()
    check_dataset()


if __name__ == "__main__":
    main()
