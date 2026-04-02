#accept name and age from the user. check if the user is a valid voter or not

name = input("enter u r name:-")
age = int(input("enter u r age:-"))

if age>=18:
    print(f"hello {name} u r a valid voter")

elif age<=18:
     print(f"hello {name} u can vote after {age} years")    

else:
     print(f"hello {name} u r not valid voter")
   
