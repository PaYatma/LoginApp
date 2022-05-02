# Load needed packages 
import os
import psycopg2

# Add URL
DATABASE_URL = os.getenv('DATABASE_URL')
# DATABASE_URL =  'postgres://postgres:mdclinicals@localhost/regulatory_docs'

# Connect to the DATABASE
conn = psycopg2.connect(DATABASE_URL)

# Create a cursor in order to execute query into the database
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute("DROP TABLE IF EXISTS Users")

# Create a new table called Documents
cursor.execute("""CREATE TABLE Users (ID SERIAL PRIMARY KEY,
        firstname VARCHAR(50), lastname VARCHAR(50), company VARCHAR(50),
        country VARCHAR(50), email VARCHAR(50) UNIQUE not null, 
        password VARCHAR(180), confirm_email Boolean not null default False,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")




# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
cursor.close()

# Close the connexion
conn.close()