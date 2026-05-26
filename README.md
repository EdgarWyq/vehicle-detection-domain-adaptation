# vehicle-detection-domain-adaptation

Nighttime vehicle detection experiments with YOLO11s, focused on reducing false positives in Sunny/Night scenes using hard-negative mining.

The project started from a concrete failure case: in night images, the detector sometimes placed large vehicle boxes on building edges, roof contours, window reflections and local light sources. The repository keeps a controlled comparison to test whether empty-label hard negatives reduce this behavior without changing the validation set.

## Overview

- Dataset subset: ICDEC `Sunny/Night`
- Model: YOLO11s
- Image size: 960
- Main comparison: original training split vs. original split plus empty-label hard negatives
- Tooling: dataset checks, split generation, training entry points, prediction export and metric comparison

## Results

The validation set is the original `Sunny/Night` validation split with 50 images. Both experiments use `yolo11s.pt`, `imgsz=960`, and disabled image augmentation. The only changed variable is whether the training set includes hard-negative samples.

| Experiment | Training set | Precision | Recall | mAP50 | mAP50-95 |
| --- | --- | ---: | ---: | ---: | ---: |
| Original baseline | Original Sunny/Night | 0.33581 | 0.17705 | 0.17374 | 0.08348 |
| Hard-negative | Original Sunny/Night + 60 empty-label hard negatives | 0.40781 | 0.19583 | 0.20361 | 0.08817 |

## Visual Comparison

The following examples show predictions from the baseline and hard-negative models on the same validation images. Low-confidence predictions are kept to make the error patterns visible.

| Case | Original baseline | Hard-negative |
| --- | --- | --- |
| test #26 | ![](docs/assets/cases/case26_original.jpg) | ![](docs/assets/cases/case26_hard_negative.jpg) |
| test #29 | ![](docs/assets/cases/case29_original.jpg) | ![](docs/assets/cases/case29_hard_negative.jpg) |
| test #46 | ![](docs/assets/cases/case46_original.jpg) | ![](docs/assets/cases/case46_hard_negative.jpg) |

## Method

The hard-negative set contains 12 no-vehicle night images collected from the target failure domain. Each image is paired with an empty YOLO label file and repeated 5 times, producing 60 extra background-only training samples.

YOLO also learns objectness on background locations. These empty-label images reduce confidence on night-scene patterns that previously looked vehicle-like to the model. In practice, this can reduce large false-positive boxes and make nearby real small targets easier to keep after NMS.

```text
Original Sunny/Night data
        |
        +-- baseline: train YOLO11s directly
        |
        +-- hard-negative: add 12 no-vehicle night images x 5 repeats
                         |
                         +-- empty .txt labels
                         +-- same model and training settings
```

Key settings:

- Model: `yolo11s.pt`
- Image size: `960`
- GPU: RTX 4060
- Augmentation: disabled
- Task focus: Sunny/Night vehicle detection

## Repository Structure

```text
.
├── vehicle_yolo/
│   ├── config.py              # paths, class names, training parameters
│   ├── dataset.py             # YOLO checks and hard-negative generation
│   ├── splits.py              # original baseline split generation
│   ├── runner.py              # train, validate and predict helpers
│   └── compare.py             # results.csv metric comparison
├── add_negative_samples.py    # hard-negative sample generation
├── prepare_original_split.py  # original baseline split generation
├── train_yolo.py              # hard-negative experiment entry point
├── train_yolo_original.py     # original baseline entry point
├── predict_compare.py         # export predictions for both models
├── compare_experiments.py     # print metric comparison
├── local.example.yaml         # dataset config template
├── docs/
│   ├── EXPERIMENTS.md
│   ├── PROJECT_NOTES.md
│   └── assets/
└── reports/
    └── compare_sunny_night.md
```

## Reproduction

Clone the repository:

```powershell
git clone https://github.com/EdgarWyq/vehicle-detection-domain-adaptation.git
cd vehicle-detection-domain-adaptation
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Prepare the ICDEC dataset locally and create `local.yaml` from `local.example.yaml`. Expected dataset layout:

```text
ICDEC_challenge_2024-main/
  images/Train/Sunny/Night
  images/Val/Sunny/Night
  labels/Train/Sunny/Night
  labels/Val/Sunny/Night
```

Check the dataset:

```powershell
.\.venv\Scripts\python.exe check_dataset.py
```

Train the hard-negative experiment:

```powershell
mkdir dataset\hard_negative_sources\sunny_night
.\.venv\Scripts\python.exe add_negative_samples.py
.\.venv\Scripts\python.exe train_yolo.py
```

Place the 12 no-vehicle night images listed in `vehicle_yolo/config.py` under `dataset/hard_negative_sources/sunny_night` before running `add_negative_samples.py`.

Train the original baseline:

```powershell
.\.venv\Scripts\python.exe prepare_original_split.py
.\.venv\Scripts\python.exe train_yolo_original.py
```

Compare metrics and export visualizations:

```powershell
.\.venv\Scripts\python.exe compare_experiments.py
.\.venv\Scripts\python.exe predict_compare.py
```

## Notes

The repository does not include the full dataset, model weights or `runs/` outputs. Only selected visualizations are kept under `docs/assets/` for demonstration.

Additional documents:

- [Experiment report](docs/EXPERIMENTS.md)
- [Project notes](docs/PROJECT_NOTES.md)
- [Comparison summary](reports/compare_sunny_night.md)
