# Load needed packages 
import psycopg2
#import mysql.connector


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

mycursor.execute("ALTER TABLE User RENAME TO Old_User;")


    
# Push (or commit) our queries into the database in order to view changes
conn.commit()
    
# Close the connexion
conn.close()