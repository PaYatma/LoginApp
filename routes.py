from flask import Blueprint
from flask_login import login_required
from flask import request, jsonify 
import psycopg2
import psycopg2.extras
from sqlalchemy import DateTime, create_engine


api = Blueprint('api', __name__, url_prefix='/Dashboard')


# Add connection
# DATABASE_URL = os.getenv('DATABASE_URL') 
DATABASE_URL = 'postgres://postgres:mdclinicals@localhost/regulatory_docs'

# Create engine
engine = create_engine(DATABASE_URL.replace("postgres://", "postgresql://"))
 

@api.route("/usa/", methods=["POST","GET"])
@login_required
def ajaxamerica():
    try:
        conn = engine.raw_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            # Retreive filters
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
