from flask import Flask,request,get_flashed_messages,redirect,render_template,url_for,g,send_file
from app import app
from app.forms import *
from flask.ext.admin import helpers

from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, PasswordField, SelectField
from wtforms.validators import Required, EqualTo

from app.models import *

class CreateGame(Form):
	name   = TextField(validators=[Required()])
	world  = SelectField(validators=[Required()])

@app.route('/game/<game_name>/explore/<x>/<y>')	
def game_explore(game_name,x,y):
	from game.game import Game
	game=Game.load(name=game_name)
	game.rebuild_caches()

	xi = int(x)
	yi = int(y)

	tiles = [[None for x in xrange(7)] for y in xrange(7)]
	for py in xrange(7):
		for px in xrange(7):
			pos = (px+xi-3,py+yi-3)
			tiles[py][px] = {
				'biome':game.world.biome_at(pos).name(),
				'x':px+xi-3,
				'y':py+yi-3,
				'owned':game.city_owning((px+xi-3,py+yi-3))!=None
			}

	owner = game.city_owning((xi,yi))
	if owner:
		owner_name = owner.name
		civ_name   = owner.civ.name
	else:
		owner_name = '<no one>'
		civ_name   = '<no one>' 
	return render_template('explore.html',
		tiles=tiles, 
        title="Games",
        biome=game.world.biome_at((xi,yi)).name(),
        owner_name=owner_name,
        civ_name=civ_name,
        game_name=game_name)

@app.route('/game/<game_name>')
def game_view(game_name):
	return render_template('game.html',
		game=Game.objects.get_or_404(name=game_name), 
        title="Games")

@app.route('/games')
def games_view():
	return render_template('games.html',
		games=Game.objects.all(), 
        title="Games")

@app.route('/game/<game_name>/delete')
def delete_game(game_name):
    game=Game.objects.get_or_404(name=game_name)
    game.delete()
    return redirect(url_for('games_view'))

class CreateGroup(Form):
	types = [
		('fighter', 'Fighter'),
		('priest',  'Priest'),
		('wizard',  'Wizard'),
		('thief',   'Thief'),
		('merchant','Merchant'),
		('hunter',  'Hunter'),
		('blacksmith','Blacksmith'),
	]
	races = [
		('human', 'Human'),
		('elf', 'Elf'),
		('dwarf', 'Dwarf'),
		('halforc', 'Half-orc'),		
	]
	name   = TextField(validators=[Required()])
	race_member_1 = SelectField(validators=[Required()],
		choices=races)
	type_member_1 = SelectField(validators=[Required()],
		choices=types)	
	race_member_2 = SelectField(validators=[Required()],
		choices=races)
	type_member_2 = SelectField(validators=[Required()],
		choices=types)
	race_member_3 = SelectField(validators=[Required()],
		choices=races)
	type_member_3 = SelectField(validators=[Required()],
		choices=types)	

@app.route('/game/<game_name>/create_group',methods=['GET','POST'])
def create_group_view(game_name):
	game = Game.objects.get_or_404(name=game_name)
	form = CreateGroup(request.form)
	if request.method == 'POST' and form.validate():
		group = Group(form.data['name'])
		group.add_member(
			form.data['type_member_1'],
			form.data['race_member_1'])
		group.add_member(
			form.data['type_member_2'],
			form.data['race_member_2'])
		group.add_member(
			form.data['type_member_3'],
			form.data['race_member_3'])
		group.save()
		return redirect(url_for('game_view',game_name=game.name))
	return render_template('creategroup.html', 
        title="Create group",
        form=form)    

@app.route('/create_game',methods=['GET','POST'])
def create_game_view():
	form = CreateGame(request.form)
	form.world.choices = [(w, w) for w in World.all_names()]
	if request.method == 'POST' and form.validate():
		game = Game(form.data['name'],form.data['world'])	
		game.save()
		return redirect(url_for('game_view',game_name=game.name))
	user = None
	#user=login.current_user 
	return render_template('creategame.html', 
        title="Create game",user=None,
        form=form)