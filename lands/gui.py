try:
    from Tkinter import *
except:
    # for Python 3
    from tkinter import *
import platec

canvas_width = 800
canvas_height = 600

def prepare_menu():
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

def show_elevation_map(p, width, height):    
    hm = platec.get_heightmap(p)
    img = PhotoImage(width=canvas_width, height=canvas_height)
    canvas.create_image(canvas_width/2,canvas_height/2, image=img, state="normal")
    for y in xrange(height):
        for x in xrange(width):
            elev = hm[y*width+x]
            if elev>0.5:
                img.put("#00ff00",(x,y))
            else:
                img.put("#0000ff",(x,y))
    
def show_plates_map(p, width, height):    
    pm = platec.get_platesmap(p)
    colors = ["#110000","#220000","#330000","#440000","#550000","#660000","#770000","#880000",
    "#990000","#aa0000","#bb0000"]
    img = PhotoImage(width=canvas_width, height=canvas_height)
    canvas.create_image(canvas_width/2,canvas_height/2, image=img, state="normal")
    for y in xrange(height):
        for x in xrange(width):
            pi = pm[y*width+x]
            img.put(colors[pi],(x,y))

def file_new():
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

    show_elevation_map(p, width, height)

    root.update_idletasks()
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