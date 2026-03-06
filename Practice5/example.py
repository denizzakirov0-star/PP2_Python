import re

s = input()

if re.fullmatch(r"ab*", s):
    print("Match")
else:
    print("No match")