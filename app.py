from flask import Flask,render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import os


app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(ROOT_DIR, 'SQLiteDB.db')

def create_connection(db_file):
    "create a connection to the sqlite db"
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

@app.route('/aboutus')
def render_newspage():
    return render_template('aboutus.html')

@app.route('/caregivers')
def render_caregiverspage():
    con = create_connection(DB_NAME)
    query = "SELECT SortID,Name,Image,Age,Location,Experience from caregivers"
    cur = con.cursor()
    cur.execute(query)
    caregivers_list = cur.fetchall()
    con.close()

    return render_template('caregivers.html',caregivers_list= caregivers_list)











if __name__ == '__main__':
    app.run()
