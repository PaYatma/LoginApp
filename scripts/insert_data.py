# Load needed packages 
import pandas as pd
import psycopg2
#import mysql.connector

# Read data from "Codes/data/" folder
mydf = pd.read_csv("data/global_tab.csv")

# Replace all missing values 'nan' in column Documents and Note by '.'
mydf["Documents"].fillna(".", inplace=True)
mydf["Note"].fillna(".", inplace=True)

# Split all row in a single list
mytuples = [tuple(mydf.iloc[i]) for i in range(mydf.shape[0])]
mytuples[0]

# Connect to the DATABASE
conn = psycopg2.connect(host="ec2-99-80-170-190.eu-west-1.compute.amazonaws.com",
                        user="edynzmbihsrqyi",
                        password="cebba2154ce00a491dbc5615d1023335ad8aa2b1924a0cf9f32f7c8c28ecc655",
                        database="d9fbv65o7volfj")

""" conn = psycopg2.connect(host="localhost",
                        user="postgres",
                        password="mdclinicals",
                        database="regulatory_docs")"""

"""conn = mysql.connector.connect(host="localhost",
                        user="root",
                        password="12Secret27@",
                        database="linh")"""

# Create a cursor in order to execute query into the database
mycursor = conn.cursor()

# Drop the table if it already exists
mycursor.execute("DROP TABLE IF EXISTS Documents")

# Create a new table called Documents
mycursor.execute("CREATE TABLE Documents (ID SERIAL PRIMARY KEY," 
        "Code VARCHAR(4), Country VARCHAR(50), Study VARCHAR(20), Tag Float(2),"
        "Created Date, Submission VARCHAR(50), Documents Text, Note Text)")

# Insert data into our table
mycursor.executemany("INSERT INTO Documents (Code, Country, Study, Tag, Created, "
                        "Submission, Documents, Note) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", mytuples)
    
# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
# Close the connexion
conn.close()