# -*- coding: utf-8 -*-

from roommates import app

from flask import session, redirect, url_for, g
from functools import wraps

@app.template_filter()
def reverse(s):
	return s[::-1]

@app.template_filter()
def link_wiki(content):
	while '==' in content:
		parts = content.split('==', 2)

		parts[1] = '<a href="' + url_for( 'wiki_page', key=parts[1] ) + '">' + parts[1].replace('_', ' ') + '</a>'
		print parts
		content = ''.join(parts)
	return content

@app.template_filter()
def currency(content):
	string = str(round(content, 2))

	numbers = string.split('.')
	print numbers
	if numbers[1] == '0':
		return numbers[0]
	else:
		if len(str(numbers[1])) == 1:
			return numbers[0] + '.' + numbers[1] + '0'
		else:
			return numbers[0] + '.' + numbers[1]

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session.get('id'):
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def login_or_test_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session.get('id') or not app.config['TESTING']:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv
