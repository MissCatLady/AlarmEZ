from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQALCHEMY_DATABASE_URI'] = 'postgresql://localhost/alarmdb'
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))

	def __init__(self, username, email, password):
		self.username = username
		self.email = email

	def __repr__(self):
		return '<User %r>' % self.username

@app.route('/')
def test():
	return "DURR"

if __name__ == '__main__':
	app.run()