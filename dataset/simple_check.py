#  创作者  ：Edgar
#  文件名  ：simple_check
#  日期   ： 2026/5/14 10:56
from pathlib import Path

root = Path("D:/python_code/PythonProject2/dataset/raw/ICDEC_challenge_2024-main")

train_images = list((root / "images" / "Train").rglob("*"))
train_labels = list((root / "labels" / "Train").rglob("*.txt"))

val_images = list((root / "images" / "Val").rglob("*"))
val_labels = list((root / "labels" / "Val").rglob("*.txt"))

image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
ignored = {"classes.txt", "train.txt", "val.txt", "valid.txt", "test.txt"}


train_images = [p for p in train_images if p.suffix.lower() in image_exts]
train_labels = [p for p in train_labels if p.name.lower() not in ignored]

val_images = [p for p in val_images if p.suffix.lower() in image_exts]
val_labels = [p for p in val_labels if p.name.lower() not in ignored]


print("训练图片数量：", len(train_images))
print("训练标签数量：", len(train_labels))
print("验证图片数量：", len(val_images))
print("验证标签数量：", len(val_labels))

print("第一张训练图片：", train_images[0])
print("第一个训练标签：", train_labels[0])

print("\n第一个标签文件内容：")
print(train_labels[0].read_text()[:300])