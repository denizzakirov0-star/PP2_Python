#nested function
def outer(x):
    def inner(y):
        return y * 2
    return inner(x) + 5

print(outer(10))