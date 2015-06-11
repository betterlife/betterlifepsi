# all the imports
from database import db_session, init_db
from flask import Flask
import flask
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from models import *
from flask import request, session, redirect, url_for, \
    abort, render_template, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'password'


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
init_db()
admin = Admin(app)
admin.add_view(ModelView(Product, db_session, category='Product',
                         menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='icon-barcode'))
admin.add_view(ModelView(ProductCategory, db_session, category='Product',
                         menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='icon-tags'))
admin.add_view(ModelView(Supplier, db_session, category='Supplier',
                         menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='icon-globe'))
admin.add_view(ModelView(PaymentMethod, db_session, category='Supplier',
                         menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='icon-transfer'))
admin.add_view(ModelView(PurchaseOrder, db_session, category='Order'))
admin.add_view(ModelView(PurchaseOrderLine, db_session, category='Order'))
admin.add_view(ModelView(SalesOrder, db_session, category='Order'))
admin.add_view(ModelView(SalesOrderLine, db_session, category='Order'))
admin.add_view(ModelView(Expense, db_session, category='Financial'))
admin.add_view(ModelView(Incoming, db_session, category='Financial'))
admin.add_view(ModelView(ExpenseStatus, db_session, category='Settings'))
admin.add_view(ModelView(ExpenseCategory, db_session, category='Settings'))
admin.add_view(ModelView(IncomingStatus, db_session, category='Settings',
                         menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='icon-usd'))
admin.add_view(ModelView(IncomingCategory, db_session, category='Settings'))


if __name__ == '__main__':
    app.run()


@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def show_entries():
    entries = Entry.query.all()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    entry = Entry()
    entry.text = request.form['text']
    entry.title = request.form['title']
    db_session.add(entry)
    db_session.commit()
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
