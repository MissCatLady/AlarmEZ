from flask import Flask, render_template, redirect, request, flash
from sqlalchemy import *
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

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


class LogIn(Form):
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])



@app.route('/', methods=('GET', 'POST'))
def index():
	signup = SignUp()
	login = LogIn()
	if request.method =='GET':
		print "nope"
		return render_template('index.html', signup=signup, login=login)
	else:

		if login.validate_on_submit():
			print "posted"
			return dashboard(login.email.data, login.email.password)
		elif signup.validate_on_submit():
			print "new user"
			return redirect('/registration')
		else:
			flash('Error')
			return render_template('index.html', signup=signup)



@app.route('/main')
def dashboard(email, password):
 	users = Table('users', metadata, autoload=True)

 	try:
		user = users.select(users.c.email == email).execute().first()
		username = user.username
		#user.email/user.password/user.app/user.uid
		#check password
		#hash salt password
		return render_template('main.html', username=username)

	except AttributeError:
		error_msg = "no user exists"
		return render_template('index.html', error_msg=error_msg)


@app.route('/registration')
def new_user(email):
	#throw user information in database
	#redirect to dashboard
	#make dashboard message for new user
	return registration

if __name__ == '__main__':
	app.run()