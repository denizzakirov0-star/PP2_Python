#Function with required and optional arguments and type annotations
def full_greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

print(full_greet("Alice"))
print(full_greet("Bob", "Hi"))