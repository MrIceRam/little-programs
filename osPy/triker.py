from tkinter import *
import random
import os

with open('./logs.txt', 'w', encoding='utf-8'):
    pass  # Файл создается/очищается автоматически

def random_color():
    # Generate a random integer between 0 and 0xFFFFFF (16777215)
    # and format it as a 6-digit hex string with a '#' prefix
    return f"#{random.randint(0, 0xFFFFFF):06x}"

root = Tk() # Tk.mainloop dont work
root.title("test")
root.geometry('700x500')
root.resizable(width=False, height=False) # запрещяет менять размер окна чибоксару
root.iconbitmap('./ice.ico')
root['bg']='#D8BFD8' #root.config(bg='blue')  # Thistle

def FirstButton():
    print("----====########====----")
    root['bg']=str(random_color())
    print("firs button")

    fd = os.open('./logs.txt', os.O_RDWR | os.O_CREAT | os.O_APPEND) #"a+" \|/ a+ dont working i dk
    os.write(fd, "23\n".encode('utf-8'))
    os.close(fd)

    with open('./logs.txt', 'r', encoding='utf-8') as f:
        content = f.read()  # Вся строка
        print(f"Весь файл:\n{content}")

label = Label(root,
              text="IceRam",
              font=("Arial",70,"bold"))

btn = Button(root,  #width=10,height=10
             text="kill", #text
             command=FirstButton, #def
             font=("Arial", 50), #шрифт и размер
             bg = str(random_color()), #bg
             activebackground="blue", # bg когда ты нажимаешь кнопку
             activeforeground=str(random_color()),
             fg=str(random_color()), # цвет текста
             ) 

img = PhotoImage(file=".\logo.png") #D:\it\little-programs\osPy\logo.png
l_logo = Label(root, image=img)


label.pack()
btn.pack()
l_logo.pack()


root.mainloop()