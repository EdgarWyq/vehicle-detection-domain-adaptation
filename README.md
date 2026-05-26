# vehicle-detection-domain-adaptation

基于 YOLO11s 的晴天夜间车辆检测实验，重点解决夜间场景中建筑边缘、屋顶轮廓、窗户反光和局部强光导致的大框误检问题。

项目围绕一个明确的失败案例展开：原始模型在夜间图像中会把背景区域误检为车辆。为验证空标签 hard-negative 样本是否能改善这一问题，项目构建了两组控制变量实验，并保持验证集不变。

## 项目概览

- 数据子集：ICDEC `Sunny/Night`
- 检测模型：YOLO11s
- 输入尺寸：960
- 对比实验：原始训练集 vs. 加入空标签 hard-negative 的训练集
- 工程内容：数据检查、负样本构造、baseline split、训练、验证、预测可视化和指标对比

## 实验结果

测试集为原始 `Sunny/Night` 验证集，共 50 张图片。两组实验均使用 `yolo11s.pt`、`imgsz=960`，关闭图像增强；唯一变量是训练集中是否加入 hard-negative 样本。

| 实验 | 训练集 | Precision | Recall | mAP50 | mAP50-95 |
| --- | --- | ---: | ---: | ---: | ---: |
| Original baseline | 原始 Sunny/Night | 0.33581 | 0.17705 | 0.17374 | 0.08348 |
| Hard-negative | 原始 Sunny/Night + 60 张空标签 hard-negative | 0.40781 | 0.19583 | 0.20361 | 0.08817 |

## 可视化对比

下面三组是同一验证图在 baseline 模型和 hard-negative 模型上的预测结果。可视化中保留了低置信度预测，便于观察误检和漏检变化。

| 样例 | Original baseline | Hard-negative |
| --- | --- | --- |
| test #26 | ![](docs/assets/cases/case26_original.jpg) | ![](docs/assets/cases/case26_hard_negative.jpg) |
| test #29 | ![](docs/assets/cases/case29_original.jpg) | ![](docs/assets/cases/case29_hard_negative.jpg) |
| test #46 | ![](docs/assets/cases/case46_original.jpg) | ![](docs/assets/cases/case46_hard_negative.jpg) |

## 方法说明

hard-negative 样本由 12 张无车辆夜间图片构成。每张图片对应一个空的 YOLO 标签文件，并重复 5 次，共得到 60 张背景样本。

YOLO 不只学习目标框，也会学习大量背景位置的 objectness。空标签 hard-negative 会降低夜间背景纹理的目标置信度，例如屋顶边缘、窗户反光和灯光区域。这样可以减少大框误检，同时降低背景框对真实小目标的干扰，使部分低照度小目标更容易在 NMS 后保留下来。

```text
原始 Sunny/Night 数据
        |
        +-- baseline：直接训练 YOLO11s
        |
        +-- hard-negative：加入 12 张无车辆夜间图像，每张重复 5 次
                         |
                         +-- 空标签 .txt
                         +-- 与 baseline 保持相同训练参数
```

关键设置：

- Model: `yolo11s.pt`
- Image size: `960`
- GPU: RTX 4060
- Augmentation: disabled
- Task focus: Sunny/Night vehicle detection

## 项目结构

```text
.
├── vehicle_yolo/
│   ├── config.py              # 路径、类别、训练参数
│   ├── dataset.py             # YOLO 数据检查与 hard-negative 构造
│   ├── splits.py              # 原始 baseline split 生成
│   ├── runner.py              # 训练、验证、预测封装
│   └── compare.py             # results.csv 指标对比
├── add_negative_samples.py    # 生成 hard-negative 样本
├── prepare_original_split.py  # 生成原始 baseline split
├── train_yolo.py              # hard-negative 实验入口
├── train_yolo_original.py     # original baseline 实验入口
├── predict_compare.py         # 导出两组模型的预测可视化
├── compare_experiments.py     # 输出指标对比
├── local.example.yaml         # 数据配置模板
├── docs/
│   ├── EXPERIMENTS.md
│   ├── PROJECT_NOTES.md
│   └── assets/
└── reports/
    └── compare_sunny_night.md
```

## 复现步骤

克隆仓库：

```powershell
git clone https://github.com/EdgarWyq/vehicle-detection-domain-adaptation.git
cd vehicle-detection-domain-adaptation
```

安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

准备 ICDEC 数据集，并参考 `local.example.yaml` 创建 `local.yaml`。期望目录结构：

```text
ICDEC_challenge_2024-main/
  images/Train/Sunny/Night
  images/Val/Sunny/Night
  labels/Train/Sunny/Night
  labels/Val/Sunny/Night
```

检查数据：

```powershell
.\.venv\Scripts\python.exe check_dataset.py
```

训练 hard-negative 实验：

```powershell
mkdir dataset\hard_negative_sources\sunny_night
.\.venv\Scripts\python.exe add_negative_samples.py
.\.venv\Scripts\python.exe train_yolo.py
```

运行 `add_negative_samples.py` 前，需要将 `vehicle_yolo/config.py` 中列出的 12 张无车辆夜间图片放到 `dataset/hard_negative_sources/sunny_night`。

训练 original baseline：

```powershell
.\.venv\Scripts\python.exe prepare_original_split.py
.\.venv\Scripts\python.exe train_yolo_original.py
```

对比指标并导出可视化：

```powershell
.\.venv\Scripts\python.exe compare_experiments.py
.\.venv\Scripts\python.exe predict_compare.py
```

## 说明

仓库不包含完整数据集、模型权重和 `runs/` 训练输出。`docs/assets/` 中仅保留少量可视化图片，用于展示实验现象。

更多内容：

- [实验报告](docs/EXPERIMENTS.md)
- [项目笔记](docs/PROJECT_NOTES.md)
- [指标对比摘要](reports/compare_sunny_night.md)

