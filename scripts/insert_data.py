# Load needed packages 
import os
import pandas as pd
'''import mysql.connector'''
import psycopg2


# Function to transform dataframe to tuples
def create_tuples(filename:str):
        data_imp =  pd.read_csv(filename)

        # Replace all missing values 'nan' in column Documents and Note by '.'
        data_imp["Documents"].fillna(".", inplace=True)
        data_imp["Note"].fillna(".", inplace=True)

        # Split all row in a single list
        mytuples = [tuple(data_imp.iloc[i]) for i in range(data_imp.shape[0])]

        return mytuples

# Run the function
mytuples_America = create_tuples(filename="data/America.csv")
mytuples_Asia = create_tuples(filename="data/Asia.csv")
mytuples_Europe = create_tuples(filename="data/Europe.csv")
mytuples_MiddleEast = create_tuples(filename="data/MiddleEast.csv")

                    
# Add connection
# DATABASE_URL =  'postgres://postgres:mdclinicals@localhost/regulatory_docs'
DATABASE_URL = os.getenv("DATABASE_URL")

# Function to create tables into the DB
def create_tabs(DB_URL:str, tab_name:str, mytuples:list):
        conn = psycopg2.connect(DB_URL)

        # Create a cursor in order to execute query into the database
        mycursor = conn.cursor()

        # Drop the table if it already exists
        mycursor.execute("DROP TABLE IF EXISTS %s" %tab_name)

        # Create a new table called Documents
        mycursor.execute("""CREATE TABLE %s (ID SERIAL PRIMARY KEY, Code VARCHAR(4),
                Country VARCHAR(50), Study VARCHAR(20), Submission VARCHAR(50), 
                        Documents Text, Note Text, Created Date)""" %tab_name)

        # Insert data into our table
        mycursor.executemany("""INSERT INTO {} (Code, Country, Study, Submission, Documents, Note, Created) 
                                        VALUES(%s,%s,%s,%s,%s,%s,%s)""".format(tab_name), mytuples)
        
        # Push (or commit) our queries into the database in order to view changes
        conn.commit()
        
        # Close the connexion
        conn.close()

# Run the function 
create_tabs(DB_URL=DATABASE_URL, tab_name='America', mytuples=mytuples_America)
create_tabs(DB_URL=DATABASE_URL, tab_name='Asia', mytuples=mytuples_Asia)
create_tabs(DB_URL=DATABASE_URL, tab_name='Europe', mytuples=mytuples_Europe)
create_tabs(DB_URL=DATABASE_URL, tab_name='MiddleEast', mytuples=mytuples_MiddleEast)
