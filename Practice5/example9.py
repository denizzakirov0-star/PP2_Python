import re

s = input()

result = re.sub(r'([A-Z])', r'_\1', s).lower()
print(result)