with open("data.txt", "a") as f:
    f.write(
"""
6. Coca Cola
    Price: 15$
    Stock: 200
    Category: drink
"""
    )
with open("data.txt") as f:
    print(f.read())