import re

s = input()

if re.fullmatch(r"a.*b", s):
    print("Match")
else:
    print("No match")