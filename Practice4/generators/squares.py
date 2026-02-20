N = int(input())
squares = (i**2 for i in range(N+1))
for sq in squares:
    print(sq)