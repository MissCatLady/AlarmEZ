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

users = Table('users', metadata, autoload=True)

class SignUp(Form):
	username = StringField('username', validators=[DataRequired()])
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])


class LogIn(Form):
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])



@app.route('/', methods=('GET', 'POST'))
def index():
	signup = SignUp(prefix="signup")
	login = LogIn(prefix="login")
	if request.method =='GET':
		print "nope"
		return render_template('index.html', signup=signup, login=login)
	else:

		if login.validate_on_submit() and request.form['btn']=='Log In':
			print "posted"
			return dashboard(login.email.data, login.password.data)
		elif signup.validate_on_submit() and request.form['btn']=='Sign Up':
			print "new user"
			#TODO validate unique email
			return new_user(signup.email.data, signup.username.data, signup.password.data)
		else:
			flash('Error')
			return render_template('index.html', signup=signup)



@app.route('/main')
def dashboard(email, password):
	#TODO SESSIONS

 	try:
		user = users.select(users.c.email == email).execute().first()
		username = user.username

		#TODOhash salt password
		#user.email/user.password/user.app/user.uid
		#TODOcheck password

		return render_template('dashboard.html', username=username)

	except AttributeError:
		error_msg = "no user exists"
		return render_template('index.html', error_msg=error_msg)


@app.route('/registration')
def new_user(email, username, password):

	#TODO: hash and salt password


	#insert user information
	user_entry = users.insert().values(username=username, email=email, 
		password=password)
	connection = engine.connect()
	res = connection.execute(user_entry)
	print res.inserted_primary_key
	connection.close()
	
	return render_template('dashboard.html', new_user="Thanks for registering!", username=username)

@app.route('/logout')
def logout():
	#TODO SESSIONS
	return redirect('/')

if __name__ == '__main__':
	app.run()