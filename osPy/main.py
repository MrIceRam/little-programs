import os
print("операционаая система",os.name)
print("текущий id процесса",os.getpid)

print(os.listdir(path="..")) #директории
x = os.listdir(path="..")
print(x[0])

os.system("tree") #cmd