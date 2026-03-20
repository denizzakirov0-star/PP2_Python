from functools import reduce

nums = [1, 2, 3, 4, 5, 6]

# map: square all numbers
squares = list(map(lambda x: x * x, nums))

# filter: keep even numbers
evens = list(filter(lambda x: x % 2 == 0, nums))

# reduce: sum of all numbers
total = reduce(lambda a, b: a + b, nums)

print("nums:", nums)
print("squares:", squares)
print("evens:", evens)
print("sum:", total)