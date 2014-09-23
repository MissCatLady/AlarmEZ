from flask import Flask, make_response, render_template, redirect, request, flash, session, url_for, escape
from sqlalchemy import *
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email
from flask.ext.scrypt import generate_password_hash, generate_random_salt, check_password_hash
import datetime

app = Flask(__name__)
online= 'postgres://paajhmcznlywin:F9igJgOjxTy9x75N6ZVUCAerzv@ec2-54-204-42-178.compute-1.amazonaws.com:5432/d1gsqisf7lo1dd'
offline='postgresql://localhost:5432/alarmdb'
engine = create_engine(online, pool_size=20, max_overflow=0)
metadata = MetaData(bind=engine)
app.config.update(
	DEBUG=True,
    SECRET_KEY='...'
)

users = Table('users', metadata, autoload=True)
friend = Table('friends', metadata, autoload=True)


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

class NewFriend(Form):
	email = StringField("E-mail", validators=[DataRequired()])


@app.route('/', methods=('GET', 'POST'))
def index():
	signup = SignUp(prefix="signup")
	login = LogIn(prefix="login")
	newfriend = NewFriend(prefix="friend")
		
	if request.method =='GET':
		user = validate_login();
		if(user):
			friends = getfriends(user.uid)
			requests = getrequests(user.uid)
			
			return render_template('dashboard.html', username=user.username, user=user, friends=friends, newfriend=newfriend, permissions=getpermissions(), requests=requests)
		
		return render_template('index.html', signup=signup, login=login)
	else:

		if login.validate_on_submit() and request.form['btn']=='Log In':
			print "posted"
			return dashboard(login.email.data, login.password.data)
		elif signup.validate_on_submit() and request.form['btn']=='Sign Up':
			print "new user"
			#TODO validate unique email
			return new_user(signup.email.data, signup.username.data, signup.password.data, newfriend)

		elif newfriend.validate_on_submit() and request.form['btn'] == 'Add Friend':
			return addfriend(newfriend)
		else:
			flash('Error')
			return render_template('index.html', signup=signup)


@app.route('/registration')
def new_user(email, username, password, newfriend):

	#salt + hashing
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
	
	resp = make_response(render_template('dashboard.html', alert="Thanks for registering!", username=username, newfriend=newfriend))
	resp.set_cookie('session_token', session_token);
	return resp;
	
@app.route('/setalarm', methods=('GET', 'POST')) 
def setalarm():

	user = validate_login()

	if (user): 

		hh = request.args.get('hours')
		mm = request.args.get('mins')
		mers = request.args.get('meridian')

		#Reformat date into unambigious string.
		#From 01/01/2000 to Jan 01 2000
		date = request.args.get('date')
		date_obj = datetime.strptime(date, "%m/%d/%Y")
		date = date_obj.strftime('%b %d %Y')
		
		uid = int(request.args.get('uid'))
		#friend = request.args.get('friend')

		time = hh + ":" + mm + " " + mers

		#Insert alarm.
		alarms = Table('alarms', metadata, autoload=True)
		alarm_entry = alarms.insert().values(uid=uid, date=date, time=time, sender=user.uid, exp='false')
		connection = engine.connect()
		res = connection.execute(alarm_entry)
		connection.close()

		#Return plain text response for ajax call.
		alarm_msg = friend + " has received an alarm for " + date + " at " + hh + ":" + mm + " " + mers
		resp = make_response(alarm_msg);
		return resp;

	return redirect("/logout")


@app.route('/alarms', methods=('GET', 'POST'))
def getalarms():
	user = request.args.get('user');
	alarms = Table('detailed_alarms', metadata, autoload=True)
	user_alarms = alarms.select(alarms.c.uid == user and alarms.c.exp == 'false').execute()
	return render_template('alarms.xml', user_alarms=user_alarms)

@app.route('/toggle', methods=('GET', 'POST'))
def toggle():

	user = validate_login()
	if (user):

		# allow msg later
		friend_uid = request.args.get('friend')
		permission_type = request.args.get('type')
		permissions = request.args.get('permission')

		if (permissions=="Yes"):
			permission = ['false', "No"]
			print permission
		elif(permissions=="No"):
			permission = ['true', "Yes"]
			print permission

		if (permission_type == "F"):
			print "updating from"

			if (len(friend.select(friend.c.id2 == friend_uid and friend.c.id1 == user.id and friend.c.request==1).execute().first()) == 0):
				permission_update = update(friend).where(friend.c.id2 == friend_uid and friend.c.id1 == user.id and friend.c.request==1).values(permission = permission[0])
				connection = engine.connect()
				connection.execute(permission_update)
				connection.close()
			else:
				permission[1] = permissions

			return make_response(permission[1])
		else:
			print "updating to"
			if (len(friend.select(friend.c.id1 == friend_uid and friend.c.id2 == user.id and friend.c.request==1).execute().first()) == 0):
				permission_update = update(friend).where(friend.c.id1 == friend_uid and friend.c.id2 == user.id and friend.c.request==1).values(permission= permission[0])
				connection = engine.connect()
				connection.execute(permission_update)
				connection.close()
			else:
				permission[1] = permissions
			return make_response(permission[1])
		
	return redirect('/logout')

@app.route('/reply', methods=('GET', 'POST'))
def reply():
	user = validate_login()
	if (user):
		uid = request.args.get('id')
		ans = request.args.get('ans')

		if (ans =="YES"):
			friend_update = update(friend).where(friend.c.id1 == uid and friend.c.id2 == user.uid).values(request=1)
		else:
			#TODO deletes
			friend_update = update(friend).where(friend.c.id1 == uid and friend.c.id2 == user.uid).values(request=0)

	return redirect('/logout')

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

def dashboard(email, password):

 	try:
		user = users.select(users.c.email == email).execute().first()
		username = user.username

		#check that passwords match
		if check_password_hash(password, user.password, user.salt):

			#set session hash
			session_token = generate_password_hash(email, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			stmt = update(users).where(users.c.email==email).values(session_token=session_token)
			connection = engine.connect()
			connection.execute(stmt)
			connection.close()

			resp = make_response(redirect('/'))
			resp.set_cookie('session_token', session_token);
			return resp;
		else:
			error_msg = "Incorrect Password"
			return render_template('/index.html', error_msg=error_msg)

	except AttributeError:
		error_msg = "no user exists"
		return render_template('index.html', error_msg=error_msg)


def addfriend(newFriend):
	user = validate_login()
	friends = getfriends(user.uid)
	requests = getrequests(user.uid)
	new_friend = users.select(users.c.email == newFriend.email.data).execute().first()

	if (new_friend and len(friend.select(friend.c.id1 == new_friend.uid and friend.c.id2 == user.uid).execute().first())==0 ):
		msg = new_friend.username + " is already in your friendlist."
		return render_template('dashboard.html', username=user.username, alert=msg, newfriend=newFriend, friends=friends, permissions=getpermissions(), requests=requests)
	elif (new_friend):
		friends = getfriends(user.uid)
		friend_entry = friend.insert().values(id1=new_friend.uid, id2=user.uid, request=2)
		connection = engine.connect()
		res = connection.execute(friend_entry)
		connection.close()
		print ["added", new_friend.username]
		msg = new_friend.username + " has been added to your friends."
		return render_template('dashboard.html', username=user.username, alert=msg, newfriend=newFriend, friends=friends, permission=getpermissions(), requests=requests)
	else:
		#TODO: SEND EMAIL
		return "friend not registered"

	
def getfriends(uid):
	#get friendlist
	friends = Table('detailed_friends', metadata, autoload=True)
	friend_choices = friends.select(friends.c.id2 == uid and friends.c.permission == True).execute()
	return friend_choices

def getpermissions():

	permissions=[]
	user = validate_login()
	friendlist = getfriends(user.uid)

	for f in friendlist:

	
		print [f.id1, user.uid]
		alert_you = friend.select(friend.c.id1 == f.id1 and friend.c.id2 == user.uid).execute().first()
		print alert_you
		
		alert_them = friend.select(friend.c.id2 == f.id1 and friend.c.id1 == user.uid).execute().first()
		print alert_them

		

		print "----"
		if (alert_them and alert_them.permission):
			alert_them = "Yes"
		else: 
			alert_them = "No"

		if (alert_you and alert_you.permission):
			alert_you = "Yes"
		else:
			alert_you = "No"


		permissions.append([f.username, alert_them, alert_you, f.id1])
	
	return permissions

def getrequests(uid):
	friends = Table('detailed_friends', metadata, autoload=True)
	friend_requests = friends.select(friends.c.id2 == uid and friends.c.request == 2).execute()
	return friend_requests





if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)