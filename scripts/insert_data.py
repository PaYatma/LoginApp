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
                    
# Add connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

# Create a cursor in order to execute query into the database
mycursor = conn.cursor()

# Drop the table if it already exists
mycursor.execute("DROP TABLE IF EXISTS Documents")

# Create a new table called Documents
mycursor.execute("""CREATE TABLE Documents (ID SERIAL PRIMARY KEY, Code VARCHAR(4),
     Country VARCHAR(50), Study VARCHAR(20), Submission VARCHAR(50), 
        Documents Text, Note Text, Tag Float(2), Created Date)""")

# Insert data into our table
mycursor.executemany("""INSERT INTO Documents (Code, Country, Study, Submission, Documents, 
                    Note, Tag, Created) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", mytuples)
    
# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
# Close the connexion
conn.close()