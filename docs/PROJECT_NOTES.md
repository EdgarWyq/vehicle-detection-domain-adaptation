# Project Notes

## Problem

The original Sunny/Night model produced several large false-positive boxes in dark urban scenes. Typical error sources included building edges, roof contours, window reflections and local light sources.

Instead of only raising the confidence threshold, this project tests whether adding empty-label hard negatives can improve the detector during training.

## Experiment Design

Two models were trained with the same settings:

- Model: YOLO11s
- Image size: 960
- Epochs: 100
- Batch size: 4
- Augmentation: disabled
- Validation split: unchanged Sunny/Night validation set

The only difference is the training set:

- `original`: original Sunny/Night training split.
- `hard-negative`: original Sunny/Night training split plus 60 empty-label hard-negative images.

The 60 hard-negative images come from 12 manually collected no-vehicle night scenes, each repeated 5 times.

## Why Empty Labels Help

YOLO learns objectness for a large number of background locations. Empty-label hard-negative images push the objectness score down for background patterns that previously looked vehicle-like to the model.

In this dataset, the hard negatives are close to the actual failure mode, so they are more useful than generic background images. They reduce large false-positive boxes and can also help real small targets survive NMS because fewer high-confidence background boxes compete with them.

## Result Summary

| Experiment | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| Original | 0.33581 | 0.17705 | 0.17374 | 0.08348 |
| Hard-negative | 0.40781 | 0.19583 | 0.20361 | 0.08817 |

The hard-negative model improves all reported metrics on the same 50-image Sunny/Night validation set.

## Limitations

- The validation set is small, so the result should be treated as a focused case study rather than a general benchmark.
- The hard-negative images come from similar viewpoints; more diverse night backgrounds would make the conclusion stronger.
- Repeating empty-label images changes the training distribution. A follow-up ablation could compare 1x, 3x, 5x and 10x repeat factors.

