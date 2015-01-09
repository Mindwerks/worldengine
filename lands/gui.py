try:
	from Tkinter import *
except:
	# for Python 3
	from tkinter import *

root = Tk()

w = Label(root, text="Hello Tkinter!")
w.pack()

root.mainloop()