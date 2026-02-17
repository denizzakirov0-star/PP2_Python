#lambda clousure
def multiplier(n):
    return lambda x: x * n

double = multiplier(2)
triple = multiplier(3)

print(double(5))
print(triple(5))