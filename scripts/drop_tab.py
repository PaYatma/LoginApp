# Load needed packages 
import os
import psycopg2

# Add URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Connect to the DATABASE
conn = psycopg2.connect(DATABASE_URL)

# Create a cursor in order to execute query into the database
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute("DROP TABLE IF EXISTS User")


# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
cursor.close()

# Close the connexion
conn.close()