from flask import Flask,request,get_flashed_messages,redirect,render_template,url_for,g,send_file
from app import app
from app.forms import *
from flask.ext.admin import helpers


from app.models import *


@app.route('/')
@app.route('/index')
def homepage():
    return render_template('index.html', 
        title="Homepage",user=None)

def serve_pil_image(pil_img):
    import StringIO
    img_io = StringIO.StringIO()
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

from worldgen.draw import biome_colors

def generate_world_img(world):
    from PIL import Image
    img = Image.new('RGBA',(world.width,world.height))
    pixels = img.load()
    for y in xrange(world.height):
        for x in xrange(world.width):
            pixels[x,y] = biome_colors[world.biome[y][x]]
    return img

@app.route('/map/<worldname>.png')
def show_map_image(worldname):
    world = WorldModel.load(worldname)
    if world==None:
        return "Request world does not exist"
    else:
        img = generate_world_img(world)
        return serve_pil_image(img)

@app.route('/world/<worldname>/delete')
def delete_world(worldname):
    World.delete(worldname)
    return redirect(url_for('worlds'))

@app.route('/world/<worldname>')
def show_world(worldname):
    world = WorldModel.load(worldname)
    if world==None:
        return "Request world does not exist"
    else:
        #return render_template('showorld.html', title="Map",user=None, world=world, cities=sorted(world.settlements, key=lambda city: city.name))
        return render_template('showorld.html', title="Map",user=None, world=world)

@app.route('/createmap',methods=['GET','POST'])
def create_world_view():
    form = CreateMapForm(request.form)
    if request.method == 'POST' and form.validate():
        world = create_map(form.data['width'],form.data['height'],form.data['name'])    
        world.save()
        return redirect('/world/%s' % world.name)
    user = None
    #user=login.current_user 
    return render_template('createmap.html', 
        title="Create map",user=None,
        form=form)

@app.route('/worlds')
def worlds():
    world_names = WorldModel.all_names()
    return render_template('worlds.html', 
        title="Worlds",user=None,
        world_names=world_names)    