#  创作者  ：Edgar
#  文件名  ：check_data
#  日期   ： 2026/5/14 01:13
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "dataset" / "raw" / "ICDEC_challenge_2024-main"

image_exts = {".jpg", ".jpeg", ".png", ".bmp"}
label_exts = {".txt"}

images_dir = DATA_ROOT / "images"
labels_dir = DATA_ROOT / "labels"

images = [p for p in images_dir.rglob("*") if p.suffix.lower() in image_exts]
labels = [p for p in labels_dir.rglob("*") if p.suffix.lower() in label_exts]

print("数据集路径：", DATA_ROOT)
print("图片数量：", len(images))
print("标签数量：", len(labels))

print("\n前 10 张图片：")
for p in images[:10]:
    print(p.relative_to(DATA_ROOT))

print("\n前 10 个标签：")
for p in labels[:10]:
    print(p.relative_to(DATA_ROOT))

# 检查一张标签内容
if labels:
    print("\n示例标签文件：", labels[0])
    print(labels[0].read_text(encoding="utf-8", errors="ignore")[:500])