try:
    from Tkinter import *
except:
    # for Python 3
    from tkinter import *

canvas_width = 800
canvas_height = 600

def file_new():
    print("Creating new map")

def file_open():
    pass

def file_save():
    pass    

def file_exit():
    root.quit()   

root = Tk()
root.wm_title("Lands - A world generator")
root.resizable(0,0)

menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=file_new)
filemenu.add_command(label="Open", command=file_open)
filemenu.add_command(label="Save", command=file_save)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=file_exit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)

w = Canvas(root, width=canvas_width, height=canvas_height)
w.pack()



root.mainloop()