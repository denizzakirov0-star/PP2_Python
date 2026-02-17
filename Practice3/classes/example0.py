#single inheritance
class Vehicle:
    def start(self):
        print("Vehicle started")

class Car(Vehicle):
    def honk(self):
        print("Car honks")

my_car = Car()
my_car.start()
my_car.honk()