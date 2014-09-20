from flask import Flask
from flask import render_template
from sqlalchemy import *
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
engine = create_engine('postgresql://localhost:5432/alarmdb', pool_size=20, max_overflow=0)
metadata = MetaData(bind=engine)
app.config.update(
	DEBUG=True,
    SECRET_KEY='...'
)


class SignUp(Form):
	username = StringField('username', validators=[DataRequired()])
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])


@app.route('/', methods=('GET', 'POST'))
def index():
	signup = SignUp()
	if signup.validate_on_submit():
		return redirect('/main')
	#users = Table('users', metadata, autoload=True)
	#example = users.select(users.c.name == 'test').execute().first()
	return render_template('index.html', signup=signup)

@app.route('/main')
def dashboard():
	return render_template('main.html')

if __name__ == '__main__':
	app.run()