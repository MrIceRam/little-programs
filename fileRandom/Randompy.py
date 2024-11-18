import random

file = open('fileRandom/RandomNUM.txt', 'w')
i = str(random.randint(1, 20))
file.write(i)

print("Python mum: ", i)