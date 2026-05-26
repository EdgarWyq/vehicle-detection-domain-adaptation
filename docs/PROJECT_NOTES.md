# 项目笔记

## 问题定位

原始 Sunny/Night 模型在夜间城市道路场景中出现了较明显的大框误检。常见误检来源包括建筑边缘、屋顶轮廓、窗户反光和局部强光。

如果只提高置信度阈值，虽然可以过滤一部分低分误检，但也会牺牲召回。本项目尝试从训练阶段处理这个问题：加入空标签 hard-negative，让模型学习这些夜间背景不是车辆。

## 实验设计

两组模型使用相同训练设置：

- Model: YOLO11s
- Image size: 960
- Epochs: 100
- Batch size: 4
- Augmentation: disabled
- Validation split: 原始 Sunny/Night 验证集

唯一变量是训练集：

- `original`：原始 Sunny/Night 训练集。
- `hard-negative`：原始 Sunny/Night 训练集 + 60 张空标签 hard-negative 样本。

60 张 hard-negative 来自 12 张无车辆夜间图片，每张重复 5 次。

## 空标签样本的作用

YOLO 会在大量背景位置上学习 objectness。空标签 hard-negative 会压低模型对特定背景纹理的目标置信度。

这批 hard-negative 与实际误检场景高度接近，因此比普通背景图更有价值。它们能减少夜间大框误检，也可能让真实小目标在 NMS 后更容易保留下来，因为高置信度背景框变少了。

## 结果摘要

| 实验 | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| Original | 0.33581 | 0.17705 | 0.17374 | 0.08348 |
| Hard-negative | 0.40781 | 0.19583 | 0.20361 | 0.08817 |

hard-negative 模型在同一组 50 张 Sunny/Night 验证图上，四项指标均高于 baseline。

## 局限

- 验证集只有 50 张图，结论更适合作为针对性案例分析，而不是通用 benchmark。
- hard-negative 图片来自相近视角，背景多样性还不够。
- 重复空标签图片会改变训练分布，后续可继续比较 1x、3x、5x、10x 等不同复制倍数。

