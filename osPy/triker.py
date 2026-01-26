from tkinter import *
import random


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
    root['bg']=str(random_color())
    print("firs button")

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
label.pack()
btn.pack()





root.mainloop()