# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import sqlite3, datetime, bcrypt
from contextlib import closing # for database-things

# create our little application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_pyfile('config.py')

from roommates.helpers import *
from roommates.classes import *
from roommates.users import *
from roommates.wiki import *

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

# VIEWS

@app.route("/")
@login_required
def index():
	g.user = User(session.get('id'))

	return render_template('index.html', user=g.user)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == 'POST':

		user = query_db('SELECT * FROM users WHERE mail = ?', [request.form['mail']], one=True)
		if user is None:
			flash('Login nicht erfolgreich.', 'error')
			return render_template('login.html')
		else:
			if bcrypt.hashpw(str(request.form['password']), str(user['password'])) == user['password']:
				session['id'] = user['id']
				flash('You are now logged in.')
				return redirect(url_for('index'))
			else:
				flash('Login nicht erfolgreich.', 'error')
				return render_template('login.html')
	else:
		return render_template('login.html')

@app.route("/logout", methods=['GET'])
@login_required
def logout():
	session.pop('id', None)
	flash('You were logged out')
	return redirect(url_for('login'))

# JUST FOR DEBUGGING

@app.route("/add_password")
def password():
	password = 'default'
	pw_hashed = bcrypt.hashpw(password, bcrypt.gensalt())

	g.db.execute('update users set password = ? where id = 1', [pw_hashed])
	g.db.commit()

	return "done"