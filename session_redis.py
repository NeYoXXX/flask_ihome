import os
from flask import Flask, session
import redis
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_TYPE"] = 'redis'
app.config["SESSION_REDIS"] = redis.Redis(host='119.3.171.42')
app.config["SESSION_USE_SIGNER"] = True
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = 3600
Session(app)

@app.route('/')
def default():
    return session.get('key', 'not set')

@app.route('/test/')
def test():
    session['key'] = 'test'
    return 'ok'

@app.route('/set/')
def set():
    arg = request.args.get('key')
    print(arg)
    session['key'] = arg
    return 'ok'


@app.route('/get/')
def get():
    return session.get('key', 'not set')


@app.route('/pop/')
def pop():
    session.pop('key')
    return session.get('key', 'not set')


@app.route('/clear/')
def clear():
    session.clear()
    return session.get('key', 'not set')

if __name__ == "__main__":
    app.run(debug=True)