from flask import Flask, url_for, render_template
app = Flask(__name__)


@app.route('/projects/')
def projects():
    return url_for('static', filename='style.css')


@app.route('/about')
def about():
    return 'The about page' + url_for('show_user_profile', username='abcdef123')


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
