from flask import Flask,request,get_flashed_messages,redirect,render_template,url_for,g,send_file
from app import app
from app.forms import *
from flask.ext.admin import helpers

from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, PasswordField
from wtforms.validators import Required, EqualTo

from app.models import *

class CreateGame(Form):
	name   = TextField(validators=[Required()])
	world  = TextField(validators=[Required()])	

@app.route('/start_game',methods=['GET','POST'])
def start_game():
	form = CreateGame(request.form)
	if request.method == 'POST' and form.validate():
		world = create_game(form.data['width'],form.data['height'],form.data['name'])	
		world.save()
		return redirect('/world/%s' % world.name)
	user = None
	#user=login.current_user 
	return render_template('createmap.html', 
        title="Create map",user=None,
        form=form)