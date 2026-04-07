# find the largest number

l = [12,45,66,3,78]

largest = l[0]
sec_largest = l[0]

for i in l:
    if i > largest:
        sec_largest = largest
        largest = i
    elif i > sec_largest:
        sec_largest = i    

    

print(sec_largest, largest)        