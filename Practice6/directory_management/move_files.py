import os, shutil

src, dst = "source", "target"
os.makedirs(dst, exist_ok=True)

for root, _, files in os.walk(src):
    for f in files:
        p = os.path.join(root, f)
        shutil.move(p, os.path.join(dst, f))