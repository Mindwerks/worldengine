from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, PasswordField
from wtforms.validators import Required, EqualTo

class CreateMapForm(Form):
	name   = TextField(validators=[Required()])
	width  = IntegerField(validators=[Required()])
	height = IntegerField(validators=[Required()])
