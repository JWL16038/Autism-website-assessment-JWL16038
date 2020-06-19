from flask import Flask,render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt


app = Flask(__name__)


@app.route('/')
def render_homepage():
    return render_template('home.html')

@app.route('/menu')
def render_newspage():
    return render_template('news.html')









if __name__ == '__main__':
    app.run()
