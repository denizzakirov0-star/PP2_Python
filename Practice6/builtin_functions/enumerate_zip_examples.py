# enumerate + zip + type checking + conversions

names = ["Ann", "Bob", "Carl"]
ages = [15, 16, 17]

# zip: paired iteration
for name, age in zip(names, ages):
    print(name, age)

# enumerate: index + value
for i, name in enumerate(names):
    print(i, name)

# type checking
values = ["10", 20, "30", 40.5]

for v in values:
    if isinstance(v, str):
        print(v, "-> int:", int(v))
    elif isinstance(v, (int, float)):
        print(v, "-> float:", float(v))

# conversion example
nums_str = ["1", "2", "3"]
nums_int = list(map(int, nums_str))

print("converted:", nums_int)