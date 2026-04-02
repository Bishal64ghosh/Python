# factorial of a number
n = int(input("plesse tell your number :-")) 

fact = 1

for i in range(1,n+1):
    fact = fact * i

    print(f"your fact is {fact}")