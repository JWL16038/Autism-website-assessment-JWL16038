from flask import Flask,render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import os

from iso3166 import countries

country_nameslist = []
country_codeslist = []

for i in countries:
    country_nameslist.append(list(i)[0])
    country_codeslist.append(list(i)[1])

app = Flask(__name__)
bcrypt = Bcrypt(app)
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
    return render_template('home.html',logged_in=is_logged_in(), session = session)

@app.route('/aboutus')
def render_aboutus():
    return render_template('aboutus.html', logged_in=is_logged_in())

@app.route('/resources')
def render_newspage():
    return render_template('resources.html', logged_in=is_logged_in())

@app.route('/contact')
def render_contactpage():
    return render_template('contactus.html', logged_in=is_logged_in())

@app.route('/caregivers')
def render_caregiverspage():
    con = create_connection(DB_NAME)
    query = "SELECT SortID,Name,Image,Age,City,Description,Experience from caregivers_page"
    cur = con.cursor()
    cur.execute(query)
    caregivers_list = cur.fetchall()
    con.close()
    return render_template('caregivers.html',caregivers_list= caregivers_list, logged_in=is_logged_in(), session = session)

@app.route('/caregivers/add/', methods=["GET","POST"])
def render_caregiversaddpage():
    error = None

    if not is_logged_in():
        return redirect('/')

    def word_count(str):
        wordcount = 0
        words = str.split()

        for word in words:
            if word:
                wordcount += 1
        return wordcount

    def sendError(error):
        return render_template('caregivers_add.html', logged_in=is_logged_in(), error=error, session=session)

    if request.method == 'POST':
        description = request.form.get('description').strip()
        experience = request.form.get('experience').strip()
        city = request.form.get('city')
        profileImage = request.form.get('ProfileImage')
        fname = session['firstname']
        lname = session['lastname']
        age = session['age']
        userID = session['userID']

        desc_count = word_count(description)
        exp_count = word_count(experience)

        if desc_count <= 20:
            error = "length for description too short"
        elif exp_count <= 20:
            error = "length for experience too short"

        con = create_connection(DB_NAME)
        query = "INSERT INTO caregivers_page(SortID,AccountID,FirstName,LastName,Image,Age,City,Description,Experience) VALUES(NULL,?,?,?,?,?,?,?,?)"
        cur = con.cursor()

        if error:
            print("error")
            con.close()
            sendError(error)
        else:
            cur.execute(query,(userID,fname,lname,profileImage,age,city,description,experience))
            print("no error")
            con.commit()
            con.close()
            return redirect('/')
    return render_template('caregivers_add.html', logged_in=is_logged_in(), error=error, session=session)

@app.route('/caregivers/book/<caregiverID>')
def addCaregiver(caregiverID):
    print('Caregivers ID: {}'.format(caregiverID))

    return redirect(request.referrer)



@app.route('/account', methods=["GET","POST"])
def render_accountpage():

    return render_template('account.html', logged_in=is_logged_in(), session=session)


@app.route('/signup')
def render_signuppage():

    if is_logged_in():
        return redirect('/')
    else:
        return render_template('signup.html',logged_in=is_logged_in())

@app.route('/signup/caregiver', methods=["GET","POST"])
def render_caregiversignup():
    error = None

    def sendError(error):
        return render_template('signup_caregiver.html', error=error)

    if request.method == 'POST':
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        age = request.form.get('age')
        countryorigin = request.form.get('country')
        ethnicity = request.form.get('ethnicity')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if len(password) < 8:
            error = "password needs to be at least 8 characters long"

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)
        query = "INSERT INTO caregiverAccounts(SortID,Firstname,Lastname,email,Age,CountryOrigin,Ethnicity,password) VALUES(NULL,?,?,?,?)"
        cur = con.cursor()

        try:
            if bcrypt.check_password_hash(hashed_password, password2):
                cur.execute(query, (fname, lname, email,age,countryorigin,ethnicity, hashed_password))
                print("Passwords match")
            else:
                error = "Passwords don't match"

        except sqlite3.IntegrityError:
            error = "Email is already taken"

        if error:
            print("error")
            con.close()
            sendError(error)
        else:
            print("no error")
            con.commit()
            con.close()
            return redirect('/')

    return render_template('signup_caregiver.html', logged_in=is_logged_in(), error=error, country_name=country_nameslist)

@app.route('/login')
def render_loginpage():
    if is_logged_in():
        return redirect('/')
    else:
        return render_template('login.html',logged_in=is_logged_in())


@app.route('/login/caregiver', methods=["GET","POST"])
def render_logincaregiver():
    error = None

    def sendError(error):
        return render_template('login_caregiver.html',  error=error,)

    if is_logged_in():
        return redirect('/')

    if request.method == "POST":
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if len(password) < 8:
            error = "password needs to be at least 8 characters long"


        con = create_connection(DB_NAME)
        query = "SELECT SortID,Firstname,Lastname,Age,password FROM caregiverAccounts WHERE email = ?"
        cur = con.cursor()
        cur.execute(query,(email,))
        user_data = cur.fetchall()
        con.close()

        try:
            userID = user_data[0][0]
            firstname = user_data[0][1]
            lastname = user_data[0][2]
            age = user_data[0][3]
            hashed_password = user_data[0][4]
            if bcrypt.check_password_hash(hashed_password, password):
                print("Passwords match")
            else:
                error = "Incorrect password"
        except IndexError:
            error = "Email or password is incorrect"

        if error:
            print("error")
            sendError(error)
        else:
            print("no error")
            session['email'] = email
            session['userID'] = userID
            session['firstname'] = firstname
            session['lastname'] = lastname
            session['age'] = age
            return redirect('/')

    return render_template('login_caregiver.html', logged_in=is_logged_in(), error=error, )


@app.route('/logout', methods=["GET","POST"])
def logout():
    session.clear()
    print("Successfully logged out")
    return redirect('/')


def is_logged_in():
    if session.get("email") is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True



if __name__ == '__main__':
    app.run()
