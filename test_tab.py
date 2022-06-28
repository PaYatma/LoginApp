import os
import re
import datetime
import psycopg2
import psycopg2.extras

from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from myforms import RegisterForm, LoginForm
from sqlalchemy import BOOLEAN, DateTime, Float, create_engine
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from flask import Flask, flash, redirect, render_template, url_for, session, request, jsonify 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user



# Add connection
# DATABASE_URL = os.getenv('DATABASE_URL') 
DATABASE_URL =  'postgres://postgres:mdclinicals@localhost/regulatory_docs'

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


@app.route('/dashboard', methods=['GET', 'POST'])
#@login_required
def dashboard():
    return render_template("myindex.html")


# Add my scripts
@app.route("/api", methods=["POST","GET"])
#@login_required
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
