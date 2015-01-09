try:
	from Tkinter import *
except:
	# for Python 3
	from tkinter import *

canvas_width = 800
canvas_height = 600

root = Tk()
root.wm_title("Lands - A world generator")
root.resizable(0,0)

w = Canvas(root, width=canvas_width, height=canvas_height)
w.pack()



root.mainloop()