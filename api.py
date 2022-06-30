import os
import re
import datetime
import psycopg2
import psycopg2.extras

from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from myforms import RegisterForm, LoginForm, ForgotForm, PasswordResetForm
from sqlalchemy import DateTime, create_engine
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user



# Add connection
DATABASE_URL = os.getenv('DATABASE_URL') 
# DATABASE_URL =  'postgres://postgres:mdclinicals@localhost/regulatory_docs'

conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config['SECURITY_PASSWORD_SALT'] = 'confirm-email'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://")
app.config['TRACK_USAGE_USE_FREEGEOIP'] = True
app.permanent_session_lifetime = timedelta(minutes=15)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=30)

mail = Mail(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)



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
    __table_args__ = {'extend_existing': True}
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
@app.route("/conf/<token>", methods=['GET', 'POST'])
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
            
    #check email
    regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,3}\b'

    if form.email.data != None and not bool((re.fullmatch(regex_email, str(form.email.data) ))):
        flash('Invalid email address!', category='error')
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        user_email = form.email.data
        _hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (user_email,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists! Please, try to login.', category='error')
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



# Forgot password
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None
    message = None
    form = ForgotForm()
    email = form.email.data
    cursor = conn.cursor()
    if form.validate_on_submit():
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user_exists = cursor.fetchone()
        if not user_exists:
            flash('There is no account with this email. Please, register first.', category='warning')
            redirect(url_for('signup'))
        else:
            s = URLSafeTimedSerializer(app.secret_key)
            token = s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
            msg = Message('Reset password request', sender='noreply.ysr@gmail.com', recipients=[email])   
            link = url_for('reset_password', token=token, _external=True)
            msg.body = '''Please, click on this link to create a new password: {}.'''.format(link)
            mail.send(msg)
            flash('A new link to reset your password is sent by email.', category='success')
    return render_template('forgot.html', title='Forgot Password', form=form, error=error, message=message)

'''# reset_password 
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form =  PasswordResetForm()
    return render_template('reset_password.html', form = form)
'''

# Confirm link for reset password
@app.route("/reset/<token>", methods=['GET', 'POST'])
def reset_password(token):
    cursor = conn.cursor()
    form = PasswordResetForm()
    s = URLSafeTimedSerializer(app.secret_key)
    email=s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=365*24*3600)
    mytoken = s.dumps(email, salt=app.secret_key)  

    if form.validate_on_submit():
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        account = cursor.fetchone()
        _hashed_pwrd = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        if form.new_password.data == form.confirm_password.data: 
            update_pwd = '''UPDATE users SET password = %s, confirm_email = %s WHERE email= %s'''
            cursor.execute(update_pwd, (_hashed_pwrd, True, account[5],))
            conn.commit() 
            flash('Your password is successfully updated.', category='success')
            redirect(url_for('login'))      
        else:
            flash('Please, correct. Passwords should be the same.', category='error')

    cursor.close()

    return render_template('reset_password.html', form = form, token=mytoken)


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
                                 and Study ILIKE %s and Submission ILIKE %s and Documents ILIKE %s and Note ILIKE %s 
                                 and Tag::text ILIKE %s and Created::text ILIKE %s LIMIT %s OFFSET %s''', 
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
                    'Submission':x[4],
                    'Documents':x[5],
                    'Note':x[6],
                    'Tag':x[7],
                    'Created':x[8]
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
