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
    query = "SELECT * from caregivers_page"
    cur = con.cursor()
    cur.execute(query)
    caregivers_list = cur.fetchall()
    con.close()


    if is_logged_in():
        usergroup = session['usergroup']
        print(usergroup)
    else:
        usergroup = 0 #usergroup with a 0 means that this person is not logged in
    return render_template('caregivers.html',caregivers_list= caregivers_list, logged_in=is_logged_in(), session=session,usergroup=usergroup)

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
        experience = request.form.get('experience').strip()
        city = request.form.get('city')
        imageTemp = request.form.get('ProfileImage')
        fname = session['firstname']
        lname = session['lastname']
        gender = session['gender']
        age = session['age']
        userID = session['userID']
        print(imageTemp)
        profileImage = imageTemp.split(".")

        if profileImage[1] == "png" or profileImage[1] == "jpg":
            print("image is a png or jpg")
            profileImage[0]
        else:
            error = "File must be a png or jpg image"

        exp_count = word_count(experience)

        if exp_count <= 20:
            error = "length for experience too short"

        con = create_connection(DB_NAME)
        query = "INSERT INTO caregivers_page(SortID,AccountID,FirstName,LastName,Gender,Image,Age,City,Experience) VALUES(NULL,?,?,?,?,?,?,?,?)"
        cur = con.cursor()

        if error:
            print("error")
            con.close()
            sendError(error)
        else:
            cur.execute(query,(userID,fname,lname,gender,profileImage,age,city,experience))
            print("no error")
            con.commit()
            con.close()
            return redirect('/')

    return render_template('caregivers_add.html', logged_in=is_logged_in(), error=error, session=session)

@app.route('/caregivers/book/', methods=["GET","POST"])
def bookCaregiver():
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
        print(error)
        return render_template('caregivers_book.html', logged_in=is_logged_in(), error=error, session=session)

    if request.method == 'POST':
        comments = request.form.get('comments').strip()
        contactdate = request.form.get('contactdate')
        contacttime = request.form.get('contacttime')
        userID = session['userID']
        fname = session['firstname']
        lname = session['lastname']
        caregiverID = session['caregiverID']
        caregiver_fname = session['caregiver_fname']
        caregiver_lname = session['caregiver_lname']
        comment_count = word_count(comments)
        if comment_count <= 20:
            error = "length for comments too short"

        if contactdate == None:
            error = "Contact date is empty"
        elif contacttime == None:
            error = "Contact time is empty"

        con = create_connection(DB_NAME)
        query = "INSERT INTO parent_caregivers(SortID,ParentID,CaregiverID,Parent_Fname,Parent_Lname,Caregiver_Fname,Caregiver_Lname,PreferedDate,PreferedTime,Comments) VALUES(NULL,?,?,?,?,?,?,?,?,?)"
        cur = con.cursor()

        if error:
            print("error")
            con.close()
            sendError(error)
        else:
            cur.execute(query, (userID,caregiverID,fname,lname,caregiver_fname,caregiver_lname,contactdate,contacttime,comments))
            print("no error")
            con.commit()
            con.close()
            return redirect('/')

    return render_template('caregivers_book.html', logged_in=is_logged_in(),error=error, session=session)





@app.route('/caregivers/book/<caregiver_pageID>')
def addCaregiver(caregiver_pageID):
    if not is_logged_in():
        return redirect('/login')
    else:
        usergroup = session['usergroup']
        if usergroup != 1:
            con = create_connection(DB_NAME)
            query = "SELECT SortID,AccountID,FirstName,LastName FROM caregivers_page WHERE SortID = ?"
            cur = con.cursor()
            cur.execute(query, (caregiver_pageID,))
            user_data = cur.fetchall()
            con.close()
            caregiverID = user_data[0][1]
            caregiver_firstname = user_data[0][2]
            caregiver_lastname = user_data[0][3]
            print(caregiverID,caregiver_firstname,caregiver_lastname)
            session['caregiverID'] = caregiverID
            session['caregiver_fname'] = caregiver_firstname
            session['caregiver_lname'] = caregiver_lastname
            return redirect('/caregivers/book/')
        else:
            return redirect(request.referrer) #already a caregiver. Caregivers can't book other caregivers. Only parents can book caregivers.



@app.route('/account', methods=["GET","POST"])
def render_accountpage():
    if not is_logged_in():
        return redirect('/login')
    else:
        usergroup = session['usergroup']
        userID = session['userID']
        if usergroup == 1: #caregiver
            parentmatched = session['parentmatched']
            if parentmatched == True:
                caregiverdata = []
                con = create_connection(DB_NAME)
                cur = con.cursor()
                query = "SELECT * FROM parent_caregivers WHERE CaregiverID = ?"
                cur.execute(query, (userID,))
                match_temp = cur.fetchall()
                query = "SELECT * FROM parentAccounts WHERE SortID = ?"
                cur.execute(query, (match_temp[0][1],))
                caregiverdata_temp = cur.fetchall()
                con.close()
                fname = caregiverdata_temp[0][1]
                lname = caregiverdata_temp[0][2]
                prefereddate = match_temp[0][3]
                preferedtime = match_temp[0][4]
                comments = match_temp[0][5]
                caregiverdata.append(fname)
                caregiverdata.append(lname)
                caregiverdata.append(prefereddate)
                caregiverdata.append(preferedtime)
                caregiverdata.append(comments)
                return render_template('account.html', logged_in=is_logged_in(), session=session, usergroup=usergroup,caregiverdata=caregiverdata)
            else:
                print("no parent matched yet")
                return render_template('account.html', logged_in=is_logged_in(), session=session, usergroup=usergroup)
        if usergroup == 2: #parent
            caregivermatched = session['caregivermatched']
            if caregivermatched == True:
                parentdata = []
                con = create_connection(DB_NAME)
                cur = con.cursor()
                query = "SELECT * FROM parent_caregivers WHERE ParentID = ?"
                cur.execute(query, (userID,))
                match_temp = cur.fetchall()
                query = "SELECT * FROM caregiverAccounts WHERE SortID = ?"
                cur.execute(query, (match_temp[0][2],))
                parentdata_temp = cur.fetchall()
                con.close()
                fname = parentdata_temp[0][1]
                lname = parentdata_temp[0][2]
                prefereddate = match_temp[0][3]
                preferedtime = match_temp[0][4]
                comments = match_temp[0][5]
                parentdata.append(fname)
                parentdata.append(lname)
                parentdata.append(prefereddate)
                parentdata.append(preferedtime)
                parentdata.append(comments)
                return render_template('account.html', logged_in=is_logged_in(), session=session, usergroup=usergroup,parentdata=parentdata)
            else:
                print("no caregiver matched yet")
                return render_template('account.html', logged_in=is_logged_in(), session=session, usergroup=usergroup)


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
        gender = request.form.get('gender')
        countryorigin = request.form.get('country')
        ethnicity = request.form.get('ethnicity')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if len(password) < 8:
            error = "password needs to be at least 8 characters long"

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)
        query = "INSERT INTO caregiverAccounts(SortID,Firstname,Lastname,Email,Gender,Age,CountryOrigin,Ethnicity,password) VALUES(NULL,?,?,?,?,?,?,?,?)"
        cur = con.cursor()

        try:
            if bcrypt.check_password_hash(hashed_password, password2):
                cur.execute(query, (fname,lname,email,gender,age,countryorigin,ethnicity,hashed_password))
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
            return redirect('/login/caregiver')

    return render_template('signup_caregiver.html', logged_in=is_logged_in(), error=error, country_name=country_nameslist)\

@app.route('/signup/parent', methods=["GET","POST"])
def render_parentsignup():
    error = None

    def sendError(error):
        return render_template('signup_parent.html', error=error)

    if request.method == 'POST':
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        age = request.form.get('age')
        gender = request.form.get('gender')
        countryorigin = request.form.get('country')
        ethnicity = request.form.get('ethnicity')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if len(password) < 8:
            error = "password needs to be at least 8 characters long"

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)
        query = "INSERT INTO parentAccounts(SortID,Firstname,Lastname,Email,Gender,Age,CountryOrigin,Ethnicity,password) VALUES(NULL,?,?,?,?,?,?,?,?)"
        cur = con.cursor()

        try:
            if bcrypt.check_password_hash(hashed_password, password2):
                cur.execute(query, (fname,lname,email,gender,age,countryorigin,ethnicity,hashed_password))
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
            return redirect('/login/parent')

    return render_template('signup_parent.html', logged_in=is_logged_in(), error=error, country_name=country_nameslist)

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
        query = "SELECT SortID,Firstname,Lastname,Gender,Age,password FROM caregiverAccounts WHERE email = ?"
        cur = con.cursor()
        cur.execute(query,(email,))
        user_data = cur.fetchall()
        con.close()

        try:
            userID = user_data[0][0]
            firstname = user_data[0][1]
            lastname = user_data[0][2]
            gender = user_data[0][3]
            age = user_data[0][4]
            hashed_password = user_data[0][5]
            if bcrypt.check_password_hash(hashed_password, password):
                print("Passwords match")
            else:
                error = "Incorrect password"
        except IndexError:
            error = "Email doesn't exist"

        if error:
            print("error")
            sendError(error)
        else:
            print("no error")
            session['email'] = email
            session['userID'] = userID
            session['firstname'] = firstname
            session['lastname'] = lastname
            session['gender'] = gender
            session['age'] = age
            session['usergroup'] = 1 # 1 is caregiver, 2 is parent

            con = create_connection(DB_NAME)
            query = "SELECT ParentID,CaregiverID FROM parent_caregivers WHERE CaregiverID = ?"
            cur = con.cursor()
            cur.execute(query, (userID,))
            match_data = cur.fetchall()
            con.close()

            try:
                parentID = match_data[0][0]
                print("parent matched")
                session['parentmatched'] = True
            except IndexError:
                print("no parent matched")
                session['parentmatched'] = False

            return redirect('/')

    return render_template('login_caregiver.html', logged_in=is_logged_in(), error=error, )

@app.route('/login/parent', methods=["GET","POST"])
def render_loginparent():
    error = None

    def sendError(error):
        return render_template('login_parent.html',  error=error,)

    if is_logged_in():
        return redirect('/')

    if request.method == "POST":
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if len(password) < 8:
            error = "password needs to be at least 8 characters long"


        con = create_connection(DB_NAME)
        query = "SELECT SortID,Firstname,Lastname,Gender,Age,password FROM parentAccounts WHERE email = ?"
        cur = con.cursor()
        cur.execute(query,(email,))
        user_data = cur.fetchall()
        con.close()

        try:
            userID = user_data[0][0]
            firstname = user_data[0][1]
            lastname = user_data[0][2]
            gender = user_data[0][3]
            age = user_data[0][4]
            hashed_password = user_data[0][5]
            if bcrypt.check_password_hash(hashed_password, password):
                print("Passwords match")
            else:
                error = "Incorrect password"
        except IndexError:
            error = "Email doesn't exist"

        if error:
            print("error")
            sendError(error)
        else:
            print("no error")
            session['email'] = email
            session['userID'] = userID
            session['firstname'] = firstname
            session['lastname'] = lastname
            session['gender'] = gender
            session['age'] = age
            session['usergroup'] = 2 # 1 is caregiver, 2 is parent

            con = create_connection(DB_NAME)
            query = "SELECT ParentID,CaregiverID FROM parent_caregivers WHERE ParentID = ?"
            cur = con.cursor()
            cur.execute(query, (userID,))
            match_data = cur.fetchall()
            con.close()

            try:
                caregiverID = match_data[0][0]
                print("caregiver matched")
                session['caregivermatched'] = True
            except IndexError:
                print("no caregiver matched")
                session['caregivermatched'] = False
            return redirect('/')

    return render_template('login_parent.html', logged_in=is_logged_in(), error=error, )


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

def get_notification():
    if session.get("email") is None:
        print("Not logged in")
        return False
    else:
        print("Logged in")
        return True



if __name__ == '__main__':
    app.run()
