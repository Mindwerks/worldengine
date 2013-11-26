from flask import Flask,request,get_flashed_messages,redirect,render_template,url_for,g
from app import app
from forms import *
from flask.ext.admin import helpers

from random import randint, choice

world = None

import atomic

atomic.ATOMDIR = '.'

name_generator = atomic.Atomic()
name_generator.atomize('atoms/general')
name_generator.atomize('atoms/mages')
name_generator.atomize('atoms/fantasy')
name_generator.atomize('atoms/dwarves')
name_generator.atomize('atoms/hobbits')
name_generator.atomize('atoms/human_m')
name_generator.atomize('atoms/human_f')
name_generator.atomize('atoms/old_phoenix')
#name_generator.atomize('atoms/orcs_wh')

@app.route('/')
@app.route('/index')
def homepage():
	return render_template('index.html', 
        title="Homepage",user=None)

def random_pos_centered_no_borders(w,h):
	x = (randint(1,w-1)+randint(1,w-1))/2
	y = (randint(1,h-1)+randint(1,h-1))/2
	return (x,y)

def random_pos_no_borders(w,h):
	x = randint(1,w-1)
	y = randint(1,h-1)
	return (x,y)

def random_land(w,h,tiles):
	x,y = random_pos_no_borders(w,h)
	if tiles[y][x]!='S':
		return (x,y)
	return random_land(w,h,tiles)

def move_in_borders(pos,w,h):
	x,y = pos
	x+=randint(-1,1)
	y+=randint(-1,1)
	if x==0:
		x=1
	if x>=(w-1):
		x=w-2
	if y==0:
		y=1
	if y>=(h-1):
		y=h-2
	return (x,y)		

def move_in_land_with_inertia(pos,w,h,tiles,vector):
	if vector==None:
		vector = (0,0)
	vx,vy = vector
	nvector = (choice([vx,vx,vx,-1,0,1]),choice([vy,vy,vy,-1,0,1]))
	x,y = pos
	nvx,nvy = nvector
	nx = x+nvx
	ny = y+nvy
	#print("X %i Y %i NV %i,%i" % (x,y,nvx,nvy))
	if tiles[ny][nx]!='S':
		npos = (nx,ny)	
		return (npos,nvector)
	else:
		return move_in_land_with_inertia(pos,w,h,tiles,vector)


def create_map(w,h,worldname):
	print("Creating a world %ix%i" % (w,h))
	
	# All the tiles contain Sea
	tiles = [['S' for x in xrange(w)] for y in xrange(h)] 

	# Tiles usable for land are all but the borders:
	nborders = w*2+h*2-4
	nlandable = w*h-nborders
	print("Landable tiles %i" % nlandable)	
	nlandstoplace = randint(0,nlandable/5)+randint(0,nlandable/5)+randint(0,nlandable/5)
	nland = nlandstoplace
	print("Land to be placed %i" % nlandstoplace)

	ncurrentcontinent = 0
	while nlandstoplace>0:
		if ncurrentcontinent==0:
			pos = random_pos_centered_no_borders(w,h)
			ncurrentcontinent= randint(2,10)*randint(1,20)
		x,y = pos
		if tiles[y][x] == 'S':
			nlandstoplace-=1
			tiles[y][x] = 'P'
			ncurrentcontinent-=1
		pos = move_in_borders(pos,w,h)

	# Place mountains
	vector = None
	ntoplace = randint(0,nland/5)+randint(0,nland/7)+randint(0,nland/7)
	print("Mountains to be placed %i" % ntoplace)
	ncurrent = 0
	while ntoplace>0:
		if ncurrent==0:
			pos = random_land(w,h,tiles)
			ncurrent = randint(1,15)
		x,y = pos
		if tiles[y][x]!='M':
			tiles[y][x] = 'M'
			ntoplace-=1
		# current mountains is reduced in every case, it avoids deadlocks
		ncurrent-=1
		(pos,vector) = move_in_land_with_inertia(pos,w,h,tiles,vector)

	# Place cities
	ncities = randint(0,nland/150)+randint(0,nland/100)+randint(0,nland/150)
	print("N cities %i" % ncities)
	cities = []
	while ncities>0:
		x,y = random_land(w,h,tiles)
		if tiles[y][x]!='C':
			tiles[y][x] = 'C'
			global name_generator
			name = name_generator.name()			
			cities.append(name)
			print('City %s' % name)
			ncities-=1

	world = World(worldname,tiles,cities)
	return world

class World:
	def __init__(self,name,tiles,cities):
		self.name = name
		self.tiles = tiles
		self.cities = cities

	def save(self):
		import pickle
		with open("worlds/%s.world" % self.name,'w') as f:
		    pickle.dump(self,f)

@app.route('/showmap')
def show_map_view():
    global world
    return render_template('showmap.html', title="Map",user=None, tiles=world.tiles)

@app.route('/createmap',methods=['GET','POST'])
def create_world_view():
	form = CreateMapForm(request.form)
	if request.method == 'POST' and form.validate():
		global world 
		world = create_map(form.data['width'],form.data['height'],form.data['name'])	
		world.save()
		return redirect('/showmap')
	user = None
	#user=login.current_user 
	return render_template('createmap.html', 
        title="Create map",user=None,
        form=form)