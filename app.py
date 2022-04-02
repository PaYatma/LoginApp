import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

myapp = Flask(__name__)

#engine = create_engine('postgresql://postgres:mdclinicals@localhost/regulatory_docs')
engine = create_engine('mysql://root:mdclinicals@localhost/linh')


@myapp.route('/')
def mydocs():
    return render_template('index.html')


@myapp.route("/api/data", methods=["POST","GET"])
def ajaxfile():
    try:
        conn = engine.raw_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]

            print(request.form)

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
            print(totalRecords) 

            ## Total number of records with filtering
            likeString = "%{}%".format(searchValue)
            print(likeString)

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


if __name__ == "__main__":
    myapp.run(debug=True)
