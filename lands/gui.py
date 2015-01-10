try:
    from Tkinter import *
except:
    # for Python 3
    from tkinter import *
import platec
from PIL import ImageTk
import PIL

canvas_width = 800
canvas_height = 600
platec_pointer = None
label_image = None
pi = None

def prepare_menu():
    menubar = Menu(root)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=file_new)
    filemenu.add_command(label="Open", command=file_open)
    filemenu.add_command(label="Save", command=file_save)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=file_exit)
    menubar.add_cascade(label="File", menu=filemenu)

    viewmenu = Menu(menubar, tearoff=0)
    viewmenu.add_command(label="Heightmap view", command=view_heightmap)
    viewmenu.add_command(label="Plates view", command=view_plates)
    menubar.add_cascade(label="View", menu=viewmenu)

    root.config(menu=menubar)

def view_heightmap():    
    global platec_pointer
    show_elevation_map(platec_pointer, canvas_width, canvas_height)

def view_plates():
    global platec_pointer
    show_plates_map(platec_pointer, canvas_width, canvas_height)

def show_elevation_map(p, width, height):    
    global label_image
    global pi
    hm = platec.get_heightmap(p)
    img = PIL.Image.new('RGBA', (width, height))
    pixels = img.load()
    for y in range(0, height):
        for x in range(0, width):            
            elev = hm[y*width + x]
            if elev>0.5:
                pixels[x, y] = (0, 200, 0, 255)
            else:
                pixels[x, y] = (0, 0, 200, 255)
    pi = ImageTk.PhotoImage(img)
    label_image = Label(root, image=pi)
    label_image.place(x=0,y=0,width=width,height=height)

def show_plates_map(p, width, height):    
    global label_image
    global pi
    pm = platec.get_platesmap(p)
    colors = ["#110000","#220000","#330000","#440000","#550000","#660000","#770000","#880000",
    "#990000","#aa0000","#bb0000"]
    img = PIL.Image.new('RGBA', (width, height))
    pixels = img.load()
    for y in xrange(height):
        for x in xrange(width):
            pi = pm[y*width+x]
            c = int((255*pi)/10)
            pixels[x,y] = (c,c,c,255)
    pi = ImageTk.PhotoImage(img)
    label_image = Label(root, image=pi)
    label_image.place(x=0,y=0,width=width,height=height)            

def file_new():
    global platec_pointer
    print("Creating new map")
    seed=1
    width=canvas_width
    height=canvas_height
    sea_level=0.65
    erosion_period=60
    folding_ratio=0.02
    aggr_overlap_abs=1000000
    aggr_overlap_rel=0.33
    cycle_count=2
    num_plates=10
    p = platec.create(seed, width, height, sea_level, erosion_period, folding_ratio,
                      aggr_overlap_abs, aggr_overlap_rel, cycle_count, num_plates)
    print("Simulation")

    platec_pointer = p

    show_elevation_map(p, width, height)

    #root.update_idletasks()
    print("Drawing")            

def file_open():
    pass

def file_save():
    pass    

def file_exit():
    root.quit()   

root = Tk()
root.wm_title("Lands - A world generator")
root.resizable(0,0)

prepare_menu()

canvas = Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

root.mainloop()