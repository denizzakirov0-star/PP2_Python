from math import tan, pi
sides = int(input("Input number of sides: "))
lenth_of_side = float(input("Input the length of a side: "))
area_of_polygon = int((sides * lenth_of_side ** 2) / (4 * tan(pi/sides)))
print(area_of_polygon)