from flask import Flask,render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import os

bcrypt = Bcrypt()

app = Flask(__name__)
app.secret_key = "16CJOH68O2M0Q1H6ZG5OW54SU3210TPM"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(ROOT_DIR, 'SQLiteDB.db')

def create_connection(db_file):
    #create a connection to the sqlite db
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

@app.route('/caregivers/book/<caregiverID>')
def addCaregiver(caregiverID):
    print('Caregivers ID: {}'.format(caregiverID))

    return redirect(request.referrer)

@app.route('/signup')
def render_signuppage():
    return render_template('signup.html')

@app.route('/signup/caregiver', methods=["GET","POST"])
def render_caregiversignup():
    if request.method == 'POST':
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        print(fname,lname,email,password,password2)

        passwordhash1 = bcrypt.generate_password_hash(password)
        print(passwordhash1)
        #passwordhash2 = bcrypt.generate_password_hash(password2)

        #checkpassword = bcrypt.check_password_hash(passwordhash1,password)
        #print(checkpassword)

        if password != password2:
            print("passwords don't match")
        elif len(password) < 8:
            print("password needs to be at least 8 characters long")
        elif len(password) > 20:
            print("password cannot be more than 20 characters long")

        con = create_connection(DB_NAME)
        query = "INSERT INTO caregiverAccounts(SortID,Firstname,Lastname,email,password) VALUES(NULL,?,?,?,?)"
        cur = con.cursor()

        try:
            cur.execute(query, (fname,lname,email,password))
        except sqlite3.IntegrityError:
            print("Email is already taken")

        con.commit()
        con.close()

    return render_template('signup_caregiver.html')



if __name__ == '__main__':
    app.run()
