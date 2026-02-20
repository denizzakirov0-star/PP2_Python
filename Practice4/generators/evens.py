n = int(input())
evens = (i for i in range(n+1) if i % 2 == 0)
for ev in evens:
    print(ev)