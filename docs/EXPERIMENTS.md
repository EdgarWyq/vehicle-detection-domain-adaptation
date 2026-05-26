# Experiment Report: Sunny/Night Hard Negative Mining

## 1. 问题背景

在晴天夜间车辆检测场景中，模型容易把以下背景区域误检为车辆：

- 建筑屋顶和墙体边缘
- 路灯、窗户、车灯等局部强光
- 暗部纹理与反光区域
- 远距离小目标附近的复杂背景

其中最明显的问题是大框误检：模型会用一个很大的 `truck`、`bike` 或 `cycle` 框覆盖建筑、道路和暗部区域。

## 2. 实验目标

验证加入无车辆 hard-negative 样本后，是否能减少夜间误检，并观察它对漏检的影响。

## 3. 数据设置

训练与验证均只使用 `Sunny/Night` 场景。

| Split | Original | Hard-negative |
| --- | ---: | ---: |
| Train images | 650 | 710 |
| Val images | 50 | 50 |
| Empty labels in train | 1 | 61 |

hard-negative 实验额外加入 12 张无车辆夜间图片，每张复制 5 份，共 60 张空标签训练样本。

验证集保持不变，避免训练/验证泄漏。

## 4. 训练设置

| 项目 | 设置 |
| --- | --- |
| Model | YOLO11s |
| Image size | 960 |
| Epochs | 100 |
| Batch | 4 |
| Device | RTX 4060 |
| Augmentation | disabled |
| Optimizer | auto |
| LR schedule | cosine |

两组实验保持相同训练参数，唯一差异是训练集是否包含 hard-negative 样本。

## 5. 指标结果

| 实验 | best epoch | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original baseline | 30 | 0.33581 | 0.17705 | 0.17374 | 0.08348 |
| Hard-negative | 20 | 0.40781 | 0.19583 | 0.20361 | 0.08817 |

hard-negative 实验在 Precision、Recall、mAP50、mAP50-95 上均高于 baseline。

## 6. 可视化结果

| Case | Original baseline | Hard-negative |
| --- | --- | --- |
| test #26 | ![](assets/cases/case26_original.jpg) | ![](assets/cases/case26_hard_negative.jpg) |
| test #29 | ![](assets/cases/case29_original.jpg) | ![](assets/cases/case29_hard_negative.jpg) |
| test #46 | ![](assets/cases/case46_original.jpg) | ![](assets/cases/case46_hard_negative.jpg) |

## 7. 现象解释

hard-negative 样本虽然没有任何车辆标签，但它会参与 YOLO 的背景 objectness 学习。模型会学到“这些夜间背景纹理不是目标”，从而降低相关区域的置信度。

这会产生两个连锁效果：

- 背景候选框分数下降，明显减少大框误检。
- 背景框不再压制或干扰真实小目标候选框，NMS 后真实目标更容易保留下来。

因此，空标签样本不只是减少误检，也可能间接减少漏检。

## 8. 局限与下一步

当前实验仍有局限：

- 验证集规模较小，只有 50 张 Sunny/Night 图片。
- hard-negative 来自同一类拍摄角度，负样本多样性仍不足。
- 复制 hard-negative 会改变训练分布，复制倍数需要继续消融。

下一步可以做：

- 比较复制倍数：1x、3x、5x、10x。
- 增加更多无车夜间场景，例如路口、停车场、居民楼外立面。
- 单独统计误检框数量、平均框面积和 false positive 类型。
- 在更高置信度阈值下比较 precision-recall tradeoff。
