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
    Game.delete(game_name)
    return redirect(url_for('games_view'))	

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