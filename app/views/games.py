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