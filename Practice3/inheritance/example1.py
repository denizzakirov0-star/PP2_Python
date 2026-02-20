def squares_gen(n):
    for i in range(n):
        yield i ** 2

for x in squares_gen(5):
    print(x)