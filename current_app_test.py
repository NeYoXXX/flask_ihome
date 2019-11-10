from flask import Flask,current_app

app = Flask(__name__)

print(app)

ctx = app.app_context()

ctx.push()


app2 = current_app

print(app2)