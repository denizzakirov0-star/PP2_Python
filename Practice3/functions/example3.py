#use the lambda and function like arguments
def apply_function(f, value):
    return f(value)

square = lambda x: x ** 2
print(apply_function(square, 5))
print(apply_function(lambda x: x + 10, 7))