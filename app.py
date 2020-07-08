from flask import Flask,render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt


app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(ROOT_DIR, 'smileDatabase.db')

def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        connection = sqlite3.connect(db_file)
        # initialise_tables(connection)
        return connection
    except Error as e:
        print(e)

    return None



@app.route('/')
def render_homepage():
    return render_template('home.html')

@app.route('/news')
def render_newspage():
    return render_template('news.html')











if __name__ == '__main__':
    app.run()
