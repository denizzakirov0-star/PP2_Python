# Skip even numbers
i = 0
while i < 6:
    i += 1
    if i % 2 == 0:
        continue
    print(i)
# prints 1 3 5
