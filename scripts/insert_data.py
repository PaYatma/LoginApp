# Load needed packages 
import os
import pandas as pd
'''import mysql.connector'''
import psycopg2

# Read data from "Codes/data/" folder
mydf = pd.read_csv("data/global_tab.csv")

# Replace all missing values 'nan' in column Documents and Note by '.'
mydf["Documents"].fillna(".", inplace=True)
mydf["Note"].fillna(".", inplace=True)

# Split all row in a single list
mytuples = [tuple(mydf.iloc[i]) for i in range(mydf.shape[0])]

# Convert variables type in mysql
'''class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        return float(value)

    def _float64_to_mysql(self, value):
        return float(value)

    def _int32_to_mysql(self, value):
        return int(value)

    def _int64_to_mysql(self, value):
        return int(value)'''

# Connect to the DATABASE
"""conn = mysql.connector.connect(host="eu-cdbr-west-02.cleardb.net",
                        user="b22cde7263420f",
                        password="4703565c",
                        database="heroku_963b7cc12121e0d")"""
                        
# DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")

DATABASE_URL = 'postgres://postgres:mdclinicals@localhost/regulatory_docs'

conn = psycopg2.connect(DATABASE_URL)

# Add the conversion
#conn.set_converter_class(NumpyMySQLConverter)

# Create a cursor in order to execute query into the database
mycursor = conn.cursor()

# Drop the table if it already exists
mycursor.execute("DROP TABLE IF EXISTS Documents")

# Create a new table called Documents
mycursor.execute("CREATE TABLE Documents (ID SERIAL PRIMARY KEY," 
        "Code VARCHAR(4), Country VARCHAR(50), Study VARCHAR(20), Tag Float(2),"
        "Created Date, Submission VARCHAR(50), Documents Text, Note Text)")

# Insert data into our table
mycursor.executemany("""INSERT INTO Documents (Code, Country, Study, Tag, Created,
                        Submission, Documents, Note) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", mytuples)
    
# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
# Close the connexion
conn.close()