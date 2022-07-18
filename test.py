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


@app.route('/', methods=['GET', 'POST'])
def dashboard():
    return render_template("test.html")


# Add America table
@app.route("/america/", methods=["POST","GET"])
def ajaxamerica():
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

            boxes_search = [searchcol0, searchcol1, searchcol2, searchcol3,
                            searchcol4, searchcol5, searchcol6]    
        
            ## Total number of records without filtering
            cursor.execute("select count(*) from america")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount[0]

            ## Total number of records with filtering
            ILIKEString = "%{}%".format(searchValue)

            cursor.execute('''SELECT count(*) as allcount from america WHERE Code ILIKE %s
                                    OR Study ILIKE %s  OR Country ILIKE %s OR Submission ILIKE %s''',
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount[0]
                        
            ## Fetch records
            if searchValue !="":
                cursor.execute('''SELECT * FROM america WHERE Code ILIKE %s 
                                    OR Country ILIKE %s OR Study ILIKE %s 
                                    OR Submission ILIKE %s LIMIT %s OFFSET %s''', 
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString, rowperpage, row,))
                docs_table = cursor.fetchall()

            elif any(boxes_search) != "":        
                cursor.execute('''SELECT * FROM america WHERE ID::text ILIKE %s and Code ILIKE %s and Country ILIKE %s
                                and Study ILIKE %s and Submission ILIKE %s and Documents ILIKE %s and Note ILIKE %s LIMIT %s OFFSET %s''', 
                (searchcol0, searchcol1, searchcol2, searchcol3, searchcol4, searchcol5, searchcol6, rowperpage, row,))
                docs_table = cursor.fetchall()
                
            else:
                cursor.execute('''SELECT * FROM america LIMIT {limit} OFFSET {offset}
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
                    'Note':x[6]
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


# Add Asia table
@app.route("/asia/", methods=["POST","GET"])
def ajaxasia():
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

            boxes_search = [searchcol0, searchcol1, searchcol2, searchcol3,
                            searchcol4, searchcol5, searchcol6]    
        
            ## Total number of records without filtering
            cursor.execute("select count(*) from asia")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount[0]

            ## Total number of records with filtering
            ILIKEString = "%{}%".format(searchValue)

            cursor.execute('''SELECT count(*) as allcount from asia WHERE Code ILIKE %s
                                    OR Study ILIKE %s  OR Country ILIKE %s OR Submission ILIKE %s''',
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount[0]
                        
            ## Fetch records
            if searchValue !="":
                cursor.execute('''SELECT * FROM asia WHERE Code ILIKE %s 
                                    OR Country ILIKE %s OR Study ILIKE %s 
                                    OR Submission ILIKE %s LIMIT %s OFFSET %s''', 
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString, rowperpage, row,))
                docs_table = cursor.fetchall()

            elif any(boxes_search) != "":        
                cursor.execute('''SELECT * FROM asia WHERE ID::text ILIKE %s and Code ILIKE %s and Country ILIKE %s
                                and Study ILIKE %s and Submission ILIKE %s and Documents ILIKE %s and Note ILIKE %s LIMIT %s OFFSET %s''', 
                (searchcol0, searchcol1, searchcol2, searchcol3, searchcol4, searchcol5, searchcol6, rowperpage, row,))
                docs_table = cursor.fetchall()
                
            else:
                cursor.execute('''SELECT * FROM asia LIMIT {limit} OFFSET {offset}
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
                    'Note':x[6]
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


# Add Europe table
@app.route("/europe/", methods=["POST","GET"])
def ajaxeurope():
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

            boxes_search = [searchcol0, searchcol1, searchcol2, searchcol3,
                            searchcol4, searchcol5, searchcol6]    
        
            ## Total number of records without filtering
            cursor.execute("select count(*) from europe")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount[0]

            ## Total number of records with filtering
            ILIKEString = "%{}%".format(searchValue)

            cursor.execute('''SELECT count(*) as allcount from europe WHERE Code ILIKE %s
                                    OR Study ILIKE %s  OR Country ILIKE %s OR Submission ILIKE %s''',
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount[0]
                        
            ## Fetch records
            if searchValue !="":
                cursor.execute('''SELECT * FROM europe WHERE Code ILIKE %s 
                                    OR Country ILIKE %s OR Study ILIKE %s 
                                    OR Submission ILIKE %s LIMIT %s OFFSET %s''', 
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString, rowperpage, row,))
                docs_table = cursor.fetchall()

            elif any(boxes_search) != "":        
                cursor.execute('''SELECT * FROM europe WHERE ID::text ILIKE %s and Code ILIKE %s and Country ILIKE %s
                                and Study ILIKE %s and Submission ILIKE %s and Documents ILIKE %s and Note ILIKE %s LIMIT %s OFFSET %s''', 
                            (searchcol0, searchcol1, searchcol2, searchcol3, searchcol4, searchcol5, searchcol6, rowperpage, row,))
                docs_table = cursor.fetchall()
                
            else:
                cursor.execute('''SELECT * FROM europe LIMIT {limit} OFFSET {offset}
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
                    'Note':x[6]
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


# Add MiddleEast table
@app.route("/middleeast/", methods=["POST","GET"])
def ajaxmiddleeast():
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

            boxes_search = [searchcol0, searchcol1, searchcol2, searchcol3,
                            searchcol4, searchcol5, searchcol6]    
        
            ## Total number of records without filtering
            cursor.execute("select count(*) from middleeast")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount[0]

            ## Total number of records with filtering
            ILIKEString = "%{}%".format(searchValue)

            cursor.execute('''SELECT count(*) as allcount from middleeast WHERE Code ILIKE %s
                                    OR Study ILIKE %s  OR Country ILIKE %s OR Submission ILIKE %s''',
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount[0]
                        
            ## Fetch records
            if searchValue !="":
                cursor.execute('''SELECT * FROM middleeast WHERE Code ILIKE %s 
                                    OR Country ILIKE %s OR Study ILIKE %s 
                                    OR Submission ILIKE %s LIMIT %s OFFSET %s''', 
                                    (ILIKEString, ILIKEString, ILIKEString, ILIKEString, rowperpage, row,))
                docs_table = cursor.fetchall()

            elif any(boxes_search) != "":        
                cursor.execute('''SELECT * FROM middleeast WHERE ID::text ILIKE %s and Code ILIKE %s and Country ILIKE %s
                                and Study ILIKE %s and Submission ILIKE %s and Documents ILIKE %s and Note ILIKE %s LIMIT %s OFFSET %s''', 
                            (searchcol0, searchcol1, searchcol2, searchcol3, searchcol4, searchcol5, searchcol6, rowperpage, row,))
                docs_table = cursor.fetchall()
                
            else:
                cursor.execute('''SELECT * FROM middleeast LIMIT {limit} OFFSET {offset}
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
                    'Note':x[6]
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
    app.run(debug=True)
