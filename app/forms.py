from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, PasswordField, SelectField
from wtforms.validators import Required, EqualTo

class CreateMapForm(Form):
    name   = TextField(validators=[Required()])
    width  = IntegerField(validators=[Required()])
    height = IntegerField(validators=[Required()])

class StartGameForm(Form):
    name  = TextField(validators=[Required()])
    race  = SelectField(choices=[('Dwarf', 'Dwarf'), ('Human', 'Human'), ('Orc', 'Orc'), ('Elf', 'Elf')])