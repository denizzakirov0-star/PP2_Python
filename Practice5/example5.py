import re

text = input()

result = re.sub(r"[ ,\.]", ":", text)
print(result)