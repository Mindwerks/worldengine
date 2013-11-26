from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('Lands')
app.debug = True
app.secret_key = 'SecretLands'
#app.config.from_object('config')
#db = SQLAlchemy(app)

#from flask.ext.login import LoginManager

#login_manager = LoginManager()
#login_manager.init_app(app)

#from app import views, models
from app.views import worlds


