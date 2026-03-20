import os
from pathlib import Path

os.makedirs("project/data/input/output/", exist_ok=True)

all_items = []
for root, dirs, files in os.walk("project"):
    for name in dirs + files:
        all_items.append(os.path.join(root, name))
print(all_items)

txts = list(Path("project").rglob("*.txt"))
pys = list(Path("project").rglob("*.py"))
print(files)