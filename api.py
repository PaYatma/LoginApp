import datetime
from logging.config import listen
from datetime import timedelta
import sqlite3
from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from myforms import RegisterForm, LoginForm
from sqlalchemy import DateTime, create_engine
import psycopg2
import psycopg2.extras
import os
import re

from werkzeug.security import generate_password_hash, check_password_hash

# DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://") #.replace("?reconnect=true", "")  
#DATABASE_URL = 'mysql://root:mdclinicals@localhost/linh'

DATABASE_URL = 'postgres://postgres:mdclinicals@localhost/regulatory_docs'#.replace("postgres://", "postgresql://")


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config['SECURITY_PASSWORD_SALT'] = 'confirm-email'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.permanent_session_lifetime = timedelta(minutes=10)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=3600*24*360)
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)
mail = Mail(app)


conn = psycopg2.connect(DATABASE_URL)

# Create engine
engine = create_engine(DATABASE_URL.replace("postgres://", "postgresql://"))


# Login settings
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# User creation
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    confirm_email = db.Column(db.Boolean, default=False)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)


# Home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
     return render_template('home.html')

# welcome page
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html', firstname = current_user.firstname)

# Profile page
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    return render_template('profile.html', 
            firstname= current_user.firstname,
            lastname = current_user.lastname,
            company = current_user.company,
            country = current_user.country,
            email = current_user.email
            )


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("index.html")


# Function for sending email 
def gettoken(email):

    s = URLSafeTimedSerializer(app.secret_key)
    token = s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
    msg = Message('Confirm Email', sender='noreply.ysr@gmail.com', recipients=[email])   
    link = url_for('confirm_link', token=token, _external=True)
    msg.body = '''Please, click on this link to confirm your email: {}.
    After 1 hour, this link will not be valid anymore.'''.format(link)
    mail.send(msg)

    return token


# Function to confirm email address
@app.route("/confirm/<token>", methods=['GET', 'POST'])
def confirm_link(token):
    form = RegisterForm()
    cursor = conn.cursor()
    user_email = form.email.data
    user_password = form.password.data

    s = URLSafeTimedSerializer(app.secret_key)
    try:
        email=s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=365*24*3600) 

        cursor.execute('SELECT * FROM Users WHERE email = %s', (user_email,))
        new_user = cursor.fetchone()


        if new_user:
            user_exists = Users(firstname=new_user[1],
                                lastname=new_user[2],
                                company=new_user[3],
                                country=new_user[4],
                                email=new_user[5],
                                password=new_user[6],
                                confirm_email=new_user[7],)

            update_user = 'UPDATE Users set confirm_email = %s where email=%s'
            cursor.execute(update_user, (True, user_password,))
            conn.commit()            

    except SignatureExpired:      
        return render_template('expired.html')
    
    cursor.close()

    return redirect(url_for('login'))



# Sign-up
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    cursor = conn.cursor()
    form = RegisterForm()

    if form.validate_on_submit():
        user_email = form.email.data
        hashed_password = bcrypt.generate_password_hash(form.password.data)#.decode('utf-8')

        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (user_email,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', form.email.data):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', form.firstname.data):
            flash('fisrtname must contain only characters and numbers!')
        elif not re.match(r'[A-Za-z0-9]+', form.lastname.data):
            flash('lastname must contain only characters and numbers!')
        elif not re.match(r'[A-Za-z0-9]+', form.company.data):
            flash('company must contain only characters and numbers!')
        elif not re.match(r'[A-Za-z0-9]+', form.country.data):
            flash('country must contain only characters and numbers!')
        
        else:
            # Account doesnt exists and the form data is valid, now insert new account into user table
            cursor.execute("""INSERT INTO users (firstname, lastname, company, country, email, password) 
                            VALUES (%s,%s,%s,%s,%s,%s)""", (form.firstname.data, form.lastname.data, 
                            form.company.data, form.country.data, form.email.data, hashed_password))
            conn.commit()
            gettoken(email=form.email.data) 

        return redirect(url_for('login')) 
    cursor.close()
    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor()
    form = LoginForm()
    
    if form.validate_on_submit():
        #user = User.query.filter_by(email=form.email.data).first()
        cursor.execute('SELECT * FROM users WHERE email = %s', (form.email.data,))
        # Fetch one record and return result
        new_user = cursor.fetchone()
        user_password = user_exists[6]

        user_exists = Users(firstname=new_user[1],
                        lastname=new_user[2],
                        company=new_user[3],
                        country=new_user[4],
                        email=new_user[5],
                        password=new_user[6],
                        confirm_email=new_user[7],)
    
        if user_exists:
            if not user_exists:
                flash('Please, confirm your email. And try again.', category='warning')
                redirect(url_for('login'))
            elif user_exists and bcrypt.check_password_hash(user_password, form.password.data):
                isremember = True if request.form.get('remember') else False
                print(isremember)
                if isremember:
                    login_user(user_exists, remember=isremember, duration=timedelta(seconds=30), fresh=True)
                else:
                    login_user(user_exists)
                return redirect(url_for('welcome'))
            else:
                flash('This password is invalid. Please, try again.', category='error')
                redirect(url_for('login'))
        else:
            flash('Email address unknown. Correct the email address. Or create an account.', category='warning')  

    cursor.close()

    return render_template('login.html', form=form)
    

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Add my scripts
@app.route("/api", methods=["POST","GET"])
@login_required
def ajaxfile():
    try:
        conn = engine.raw_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            # REtreive filters
            searchcol0 = "%{}%".format(request.form['columns[0][search][value]'])
            searchcol1 = "%{}%".format(request.form['columns[1][search][value]'])
            searchcol2 = "%{}%".format(request.form['columns[2][search][value]'])
            searchcol3 = "%{}%".format(request.form['columns[3][search][value]'])
            searchcol4 = "%{}%".format(request.form['columns[4][search][value]'])
            searchcol5 = "%{}%".format(request.form['columns[5][search][value]'])
            searchcol6 = "%{}%".format(request.form['columns[6][search][value]'])
            searchcol7 = "%{}%".format(request.form['columns[7][search][value]'])
            searchcol8 = "%{}%".format(request.form['columns[8][search][value]'])

            boxes_search = [searchcol0, searchcol1, searchcol2, 
                            searchcol3, searchcol4, searchcol5,
                            searchcol6, searchcol7, searchcol8]    
        
            ## Total number of records without filtering
            cursor.execute("select count(*) from Documents")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount[0]

            ## Total number of records with filtering
            likeString = "%{}%".format(searchValue)

            cursor.execute('''SELECT count(*) as allcount from Documents WHERE Code LIKE %s
                                     OR Study LIKE %s  OR Country LIKE %s OR Submission LIKE %s''',
                                    (likeString, likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount[0]
                        

            ## Fetch records
            if searchValue !="":
                cursor.execute('''SELECT * FROM Documents WHERE Code LIKE %s 
                                    OR Country LIKE %s OR Study LIKE %s 
                                    OR Submission LIKE %s LIMIT %s OFFSET %s''', 
                                    (likeString, likeString, likeString, likeString, rowperpage, row,))
                docs_table = cursor.fetchall()

            elif any(boxes_search) != "":        
                cursor.execute('''SELECT * FROM Documents WHERE ID LIKE %s and Code LIKE %s and Country LIKE %s
                                 and Study LIKE %s and Tag LIKE %s and Created LIKE %s and Submission LIKE %s
                                 and Documents LIKE %s and Note LIKE %s LIMIT %s OFFSET %s''', 
                (searchcol0, searchcol1, searchcol2, searchcol3, searchcol4, searchcol5, searchcol6,
                         searchcol7, searchcol8, rowperpage, row,))
                docs_table = cursor.fetchall()
                
            else:
                cursor.execute('''SELECT * FROM Documents LIMIT {limit} OFFSET {offset}
                                    '''.format(limit=rowperpage, offset=row))
                docs_table = cursor.fetchall()  

            # Sort table
            direction = request.form.get('order[0][dir]')
            col_index = request.form.get('order[0][column]', type=int)
            col_name = request.form.get(f'columns[{col_index}][data]')
           
            if direction == "asc":
                docs_table = sorted(docs_table, key= lambda x: x[col_index], reverse=False)
            else:
                docs_table = sorted(docs_table, key= lambda x: x[col_index], reverse=True)

            data = []
            for x in docs_table:
                data.append({
                    'ID':x[0],
                    'Code':x[1],
                    'Country':x[2],
                    'Study':x[3],
                    'Tag':x[4],
                    'Created':x[5],
                    'Submission':x[6],
                    'Documents':x[7],
                    'Note':x[8]
                })

  
            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response) 

    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()


if __name__=='__main__':
    app.run()
   