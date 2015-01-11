try:
    from Tkinter import *
except:
    # for Python 3
    from tkinter import *
import platec
try:
    from lands.draw import *
except:
    from draw import *
from PIL import ImageTk
import PIL

canvas_width = 800
canvas_height = 600
platec_pointer = None
label_image = None
pi = None
current_view = "heightmap"

def cos(x):
    import math
    return math.cos(x/180 * 3.14)    

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
    viewmenu.add_command(label="Plates and elevation view", command=view_plates_and_elevation)
    menubar.add_cascade(label="View", menu=viewmenu)

    platesmenu = Menu(menubar, tearoff=0)
    platesmenu.add_command(label="1 Step", command=plates_1)
    platesmenu.add_command(label="10 Steps", command=plates_10)
    platesmenu.add_command(label="100 Steps", command=plates_100)
    platesmenu.add_command(label="Complete simulation", command=plates_to_end)
    menubar.add_cascade(label="Plates", menu=platesmenu)    

    root.config(menu=menubar)

def _plates(n):    
    global platec_pointer
    global current_view
    if n==-1:
        while platec.is_finished(platec_pointer) == 0:
            platec.step(platec_pointer)
    else:
        for i in range(0,n):
            platec.step(platec_pointer)
    if current_view=="heightmap":
        view_heightmap()
    elif current_view=="plates_and_elevation":
        view_plates_and_elevation()
    else:
        view_plates()

def plates_1():
    _plates(1)

def plates_10():
    _plates(10)

def plates_100():
    _plates(100)

def plates_to_end():
    _plates(-1)

def view_heightmap():    
    global platec_pointer
    show_elevation_map(platec_pointer, canvas_width, canvas_height)

def view_plates():
    global platec_pointer
    show_plates_map(platec_pointer, canvas_width, canvas_height)

def view_plates_and_elevation():
    global platec_pointer
    show_plates_and_elevation_map(platec_pointer, canvas_width, canvas_height)

def show_elevation_map(p, width, height):    
    global label_image
    global pi
    global current_view
    current_view = "heightmap"
    hm = platec.get_heightmap(p)
    img = draw_simple_elevation_on_image(hm, True, width, height)
    pi = ImageTk.PhotoImage(img)
    label_image = Label(root, image=pi)
    label_image.place(x=0,y=0,width=width,height=height)

def hsi_to_rgb(hue, saturation, intensity):
    h = H = hue % 360
    S = saturation
    I = intensity
    IS = saturation * intensity

    if h==0:
        R = I + 2 * IS
        G = I - IS
        B = I - IS
    elif 0 < H and H < 120:
        R = I + IS*cos(H)/cos(60-H)
        G = I + IS*(1 - cos(H)/cos(60-H))
        B = I - IS
    elif H == 120:
        R = I - IS
        G = I + 2 * IS
        B = I - IS
    elif 120 < H and H < 240:
        R = I - IS
        G = I + ((IS*cos(H-120))/cos(180-H))
        B = I + IS*(1 - cos(H-120)/cos(180-H))
    elif H == 240:
        R = I - IS
        G = I - IS
        B = I + 2 * IS
    elif 240 < H and H < 360:
        R = I + IS*(1 - cos(H-240)/cos(300-H))
        G = I - IS
        B = I + IS*cos(H-240)/cos(300-H)    
    else:
        raise "Unexpected"
    return (int(R), int(G), int(B))

def show_plates_and_elevation_map(p, width, height):    
    global label_image
    global pi
    global current_view
    current_view = "plates_and_elevation"
    hm = platec.get_heightmap(p)
    pm = platec.get_platesmap(p)

    n_plates = 1 + max(pm)
    max_elev = max(hm)
    min_elev = min(hm)
    elev_delta = max_elev - min_elev

    img = PIL.Image.new('RGBA', (width, height))
    pixels = img.load()
    for y in range(0, height):
        for x in range(0, width):          
            h = pm[y*width+x]*(360/n_plates)
            s = 1.0
            i = 255.0 * ((hm[y*width+x]-min_elev)/elev_delta)
            pixels[x, y] = hsi_to_rgb(h,s,i)

    pi = ImageTk.PhotoImage(img)
    label_image = Label(root, image=pi)
    label_image.place(x=0,y=0,width=width,height=height)    

def show_plates_map(p, width, height):    
    global label_image
    global pi
    global current_view
    current_view = "platesmap"
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