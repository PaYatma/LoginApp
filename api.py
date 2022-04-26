import datetime
from datetime import timedelta
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

DATABASE_URL = os.getenv('DATABASE_URL') 


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config['SECURITY_PASSWORD_SALT'] = 'confirm-email'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://")

app.permanent_session_lifetime = timedelta(minutes=15)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=30)
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
login_manager.login_message = "Please, log in to acces this page."


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
   
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


# function to create mysqk user
def create_user(id, connexion):
    cursor = connexion.cursor() 
    cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
    user_exists = cursor.fetchone()
    user = Users(id = id,
                firstname=user_exists[1],
                lastname=user_exists[2],
                company=user_exists[3],
                country=user_exists[4],
                email=user_exists[5],
                password=user_exists[6],
                confirm_email=user_exists[7])
    cursor.close()
    return user


# Home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
     return render_template('home.html')

# welcome page
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html', name='Guest')

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
    msg.body = '''Please, click on this link to confirm your email: {}.'''.format(link)
    mail.send(msg)

    return token


# Function to confirm email address
@app.route("/confirm/<token>", methods=['GET', 'POST'])
def confirm_link(token):
    form = RegisterForm()
    cursor = conn.cursor()
    s = URLSafeTimedSerializer(app.secret_key)

    try:
        email=s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=365*24*3600)

        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user_exists = cursor.fetchone()

        if user_exists:
            update_user = '''UPDATE users SET confirm_email = %s WHERE email= %s'''
            cursor.execute(update_user, (True, user_exists[5],))
            conn.commit()
            return redirect(url_for('welcome'))

    except SignatureExpired:      
        return render_template('expired.html')
        
    cursor.close()

    return redirect(url_for('home'))



# Sign-up
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    cursor = conn.cursor()
    form = RegisterForm()

    if form.validate_on_submit():
        user_email = form.email.data
        _hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        #check email
        regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (user_email,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists!', category='error')
        elif not (re.fullmatch(regex_email, form.email.data)):
            flash('Invalid email address!', category='error')
            return render_template('register.html', form=form) 
        else:
            # Account doesnt exists and the form data is valid, now insert new account into user table
            cursor.execute("""INSERT INTO users (firstname, lastname, company, country, email, password) 
                            VALUES (%s,%s,%s,%s,%s,%s)""", (form.firstname.data, form.lastname.data, 
                            form.company.data, form.country.data, form.email.data, _hashed_password))
            conn.commit()
            gettoken(email=form.email.data) 

            flash('Please, check your email for confirmation.', category='success')
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
        user_exists = cursor.fetchone()
        
        if user_exists:
            user = create_user(id=user_exists[0], connexion=conn)
            if not user_exists[7]:
                flash('Please, confirm your email. And try again.', category='warning')
                redirect(url_for('login'))
            elif user_exists and bcrypt.check_password_hash(user_exists[6], form.password.data):
                login_user(user)
                return redirect(url_for('home'))
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
    session.pop('logged_in', None)
    session.pop('active_user', None)
    flash('You are logged out!', category='success')
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
            ILIKEString = "%{}%".format(searchValue)

            cursor.execute('''SELECT count(*) as allcount from Documents WHERE Code ILIKE %s
                                     OR Study ILIKE %s  OR Country ILIKE %s OR Submission ILIKE %s''',
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount[0]
                        

            ## Fetch records
            if searchValue !="":
                cursor.execute('''SELECT * FROM Documents WHERE Code ILIKE %s 
                                    OR Country ILIKE %s OR Study ILIKE %s 
                                    OR Submission ILIKE %s LIMIT %s OFFSET %s''', 
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString, rowperpage, row,))
                docs_table = cursor.fetchall()

            elif any(boxes_search) != "":        
                cursor.execute('''SELECT * FROM Documents WHERE ID::text ILIKE %s and Code ILIKE %s and Country ILIKE %s
                                 and Study ILIKE %s and Tag::text ILIKE %s and Created::text ILIKE %s and Submission ILIKE %s
                                 and Documents ILIKE %s and Note ILIKE %s LIMIT %s OFFSET %s''', 
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
   