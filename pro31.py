# find the greatest element and print its index too

l=[23,57,45,78,90,334,9014]

largest=l[0]
index=0

for i in range(len(l)):
    if l[i] > largest:
        largest = l[i]
        index = i

print(f"your largest number is {largest} at index {index}")        
