from flask import Flask, make_response, redirect, request

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


@app.route('/user/<name>')
def name(name):
    return f'<h1>Hello {name.capitalize()}</h1>'


@app.route('/user-agent')
def check_user_agent():
    user_agent = request.headers.get('User-Agent')
    return f'Your browser is {user_agent}.'


@app.route('/getting-response')
def get_response():
    res = make_response('<p>This document carries a cookie!</p>')
    res.set_cookie('this is a cookie', 'biscuit')
    return res


@app.route('/this-is-redirect')
def get_redirect():
    return redirect('https://google.com')


if __name__ == '__main__':
    app.run(debug=True)
