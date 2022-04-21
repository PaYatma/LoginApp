# Load needed packages 
import mysql.connector

# Connect to the DATABASE
conn = mysql.connector.connect(host="eu-cdbr-west-02.cleardb.net",
                        user="b22cde7263420f",
                        password="4703565c",
                        database="heroku_963b7cc12121e0d")

# add cursor
mycursor = conn.cursor()

# Drop the table if it already exists
mycursor.execute("DROP TABLE IF EXISTS User")

# Create a new table called Documents
mycursor.execute("""CREATE TABLE User (ID SERIAL PRIMARY KEY, firstname VARCHAR(50), 
                    lastname VARCHAR(50), company VARCHAR(50), email VARCHAR(50) unique, 
                    password VARCHAR(120), confirm_email Boolean, created_date timestamp not null default now()""")

    
# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
# Close the connexion
conn.close()