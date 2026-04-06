# create a random number guessing game with python

import random

num = random.randint(1,10)

tries = 0

while True:
    guess = int(input("please guess your number between 1 to 10 "))
    if num == guess:
        tries += 1
        print(f"your right you guessed the number is {tries}")
        break
    elif num<guess:
        print("go little lower")
        tries +=1

    elif num < guess:
        print("go little lower")
        tries +=1

    else:
        tries +=1
        print("u r dum as fuck")  
    

