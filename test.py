from flask import Flask, make_response, render_template, redirect, request, flash, session, url_for, escape
from sqlalchemy import *
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from flask.ext.scrypt import generate_password_hash, generate_random_salt, check_password_hash
import datetime

app = Flask(__name__)
engine = create_engine('postgresql://localhost:5432/alarmdb', pool_size=20, max_overflow=0)
metadata = MetaData(bind=engine)
app.config.update(
	DEBUG=True,
    SECRET_KEY='...'
)

users = Table('users', metadata, autoload=True)


def validate_login():
	session_token = request.cookies.get('session_token')
	if(session_token != ""):
		user = users.select(users.c.session_token == session_token).execute().first()
		return user
	return None

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
		user = validate_login();
		if(user):
			return render_template('dashboard.html', username=user.username)
		
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

 	try:
		user = users.select(users.c.email == email).execute().first()
		username = user.username

		if check_password_hash(password, user.password, user.salt):
			session_token = generate_password_hash(email, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			stmt = update(users).where(users.c.email==email).values(session_token=session_token)
			connection = engine.connect()
			connection.execute(stmt)
			connection.close()

			resp = make_response(render_template('dashboard.html', username=username))
			resp.set_cookie('session_token', session_token);
			return resp;
		else:
			error_msg = "Incorrect Password"
			return render_template('/index.html', error_msg=error_msg)

	except AttributeError:
		error_msg = "no user exists"
		return render_template('index.html', error_msg=error_msg)
	

@app.route('/registration')
def new_user(email, username, password):

	#selt + hashing
	salt = generate_random_salt()
	password = generate_password_hash(password, salt)
	session_token = generate_password_hash(email, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	#insert user information
	user_entry = users.insert().values(username=username, email=email, 
		password=password, salt=salt, session_token = session_token)
	connection = engine.connect()
	res = connection.execute(user_entry)
	print res.inserted_primary_key
	connection.close()
	
	resp = make_response(render_template('dashboard.html', new_user="Thanks for registering!", username=username))
	resp.set_cookie('session_token', session_token);
	return resp;

@app.route('/logout')
def logout():

	user = validate_login();
	if(user):
		stmt = update(users).where(users.c.email==user.email).values(session_token="")
		connection = engine.connect()
		connection.execute(stmt)
		connection.close()

	resp = make_response(redirect('/'))
	resp.set_cookie('session_token', '');
	return resp;

if __name__ == '__main__':
	app.run()