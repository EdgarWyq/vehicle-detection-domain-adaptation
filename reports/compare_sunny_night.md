# Sunny/Night 对比实验结果

测试集：`splits/sunny_night_original_val.txt`

测试图像数：50

## 指标对比

| 实验 | best epoch | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| hard-negative | 20 | 0.40781 | 0.19583 | 0.20361 | 0.08817 |
| original | 30 | 0.33581 | 0.17705 | 0.17374 | 0.08348 |

## 可视化输出

| 实验 | 可视化目录 | 图像数 | 有检测标签文件数 |
| --- | --- | ---: | ---: |
| hard-negative | `runs/detect/predict_sunny_night_hardneg` | 50 | 44 |
| original | `runs/detect/predict_sunny_night_original` | 50 | 28 |

## 当前观察

hard-negative 实验在 Precision、Recall、mAP50 和 mAP50-95 上均高于 original baseline。  
但它在 50 张测试图中产生了更多有检测结果的标签文件，建议逐张对照两个可视化目录，重点看夜间灯光、屋顶边缘、窗户反光区域是否仍有误检。
