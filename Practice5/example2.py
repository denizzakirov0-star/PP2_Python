import re

text = input()

result = re.findall(r"[a-z]+_[a-z]+", text)
print(result)