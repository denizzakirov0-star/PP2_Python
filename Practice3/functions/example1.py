#*args - positional arguments, **kwargs - dictionary argument like key - value
def process_data(*args, **kwargs):
    total = sum(args)
    for key, value in kwargs.items():
        print(f"{key}: {value}")
    return total

result = process_data(1, 2, 3, name="Alice", age=25)
print("Total:", result)