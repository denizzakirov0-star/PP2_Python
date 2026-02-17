#lambda also can usage in other functions like separator 
numbers = [1, 2, 3, 4, 5]

squared = list(map(lambda x: x ** 2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))

print("Squared:", squared)
print("Evens:", evens)
