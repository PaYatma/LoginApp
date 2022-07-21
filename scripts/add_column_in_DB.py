 # Load needed packages 
import os
import psycopg2

# Add URL
# DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL =  'postgres://postgres:mdclinicals@localhost/regulatory_docs'

# Connect to the DATABASE
conn = psycopg2.connect(DATABASE_URL)

# Create a cursor in order to execute query into the database
cursor = conn.cursor()

# Add profile_pic column
cursor.execute("ALTER TABLE Users ADD COLUMN profile_pic VARCHAR")

# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
cursor.close()

# Close the connexion
conn.close()