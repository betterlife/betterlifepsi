# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
import os



# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'password'
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


# create our little application :)
app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(__name__)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=False)
    text = db.Column(db.String(4096), unique=False)

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<Entry %r>' % self.title

if __name__ == '__main__':
    app.run()


@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.route('/')
def show_entries():
    entries = Entry.query.all()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    entry = Entry(request.form['title'], request.form['text'])
    db.session.add(entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
