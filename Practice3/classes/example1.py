#multilevel inheritance
class Animal:
    def eat(self):
        print("Animal eats")

class Mammal(Animal):
    def walk(self):
        print("Mammal walks")

class Dog(Mammal):
    def bark(self):
        print("Dog barks")

my_dog = Dog()
my_dog.eat()
my_dog.walk()
my_dog.bark()