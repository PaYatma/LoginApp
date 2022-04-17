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
from sqlalchemy import DateTime
import psycopg2
import os


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config['SECURITY_PASSWORD_SALT'] = 'confirm-email'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=3600*24*360)
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)
mail = Mail(app)

app.permanent_session_lifetime = timedelta(minutes=10)


# Create engine
engine_options = app.config['SQLALCHEMY_ENGINE_OPTIONS']
url = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')
engine = db.create_engine(sa_url=url, engine_opts=engine_options)

# Login settings
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User creation
class User(db.Model, UserMixin):
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
    s = URLSafeTimedSerializer(app.secret_key)
    try:
        email=s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600*24*360) 
        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            user_exist.confirm_email = True
            db.session.commit()
    except SignatureExpired:      
        return render_template('expired.html')

    return redirect(url_for('login'))


# Sign-up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        company=form.company.data,
                        country=form.country.data,
                        email=form.email.data, 
                        password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            gettoken(email=form.email.data)

        except:
            flash("This email address already exists. Please, login from here.", category='info')
            return redirect(url_for('login')) 

        return redirect(url_for('login')) 

    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    session.permanent = True        
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
    
        if user:
            if not user.confirm_email:
                flash('Please, confirm your email. And try again.', category='warning')
                redirect(url_for('login'))
            elif user.confirm_email and bcrypt.check_password_hash(user.password, form.password.data):
                isremember = True if request.form.get('remember') else False
                print(isremember)
                if isremember:
                    login_user(user, remember=isremember, duration=timedelta(seconds=30), fresh=True)
                else:
                    login_user(user)
                return redirect(url_for('welcome'))
            else:
                flash('This password is invalid. Please, try again.', category='error')
                redirect(url_for('login'))
        else:
            flash('Email address unknown. Correct the email address. Or create an account.', category='warning')  

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
    app.run(debug=False)
   