import mysql.connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth.authentication import Authenticate


auth = Authenticate()

#establishing the connection to DB
conn = mysql.connector.connect(
   option_files='database/connect.cnf',
   database='WORKORDERS'
)

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Dropping WO table if already exists.
cursor.execute("DROP TABLE IF EXISTS WO")

#Creating table as per requirement
sql1 = '''
CREATE TABLE WO (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    department VARCHAR(60),
    signature VARCHAR(60),
    ticket_status CHAR(30),
    urgent_status CHAR(30),
    date VARCHAR(30),
    notes LONGTEXT,
    tech_notes LONGTEXT,
    complete_date VARCHAR(30)
);
'''
cursor.execute(sql1)

cursor.execute("DROP TABLE IF EXISTS users")

sql3 ='''CREATE TABLE users(
   username VARCHAR(60),
   password VARCHAR(280)
)'''
cursor.execute(sql3)


cursor.execute("DROP TABLE IF EXISTS departments")

sql4 ='''CREATE TABLE departments(
   department VARCHAR(60)
)'''
cursor.execute(sql4)


# Urgent status boolean logic: Urgent = 1, Not Urgent = 0

data_to_insert = [
      ('Michael Arthur', 'Cosmic', '', 'Submitted', 'Urgent', '2024-01-14 00:10:02', 'Lane 5 has missing pin', '', ''),
      ('Ben Davis', 'Billiards', '', 'Complete', '     ', '2024-01-13 00:10:02', 'Pac-Man controller doesnt turn', '', ''), 
      ('Warren Kerr', 'Q-Bar', '', 'Submitted', '     ', '2024-01-15 00:10:02', 'Soda machine doesnt dispense drink', '', ''), 
      ('Mark Regan', 'Cafe', '', 'Submitted', 'Urgent', '2024-01-12 00:10:02', 'Lane 8 fails to return bowling balls', '', ''), 
      ('Saadaq Sufi', 'Pizza', '', 'Submitted', '     ', '2024-01-11 00:10:02', 'Ice machine is broken', '', ''),
      ('Michael Arthur', 'Boardwalk', '', 'Initiated', 'Urgent', '2024-01-10 00:10:02', 'Lane 5 has missing pin', '', ''),
      ('Ben Davis', 'Bowl', '', 'Initiated', '     ', '2024-01-09 00:10:02', 'Pac-Man controller doesnt turn', '', ''), 
      ('Warren Kerr', 'Pizza', '', 'Submitted', '     ', '2024-01-08 00:10:02', 'Soda machine doesnt dispense drink', '', ''), 
      ('Mark Regan', 'Billiards', '', 'Submitted', 'Urgent', '2024-01-07 00:10:02', 'Lane 8 fails to return bowling balls', '', ''), 
      ('Saadaq Sufi', 'Pizza', '', 'Submitted', '     ', '2024-01-06 00:10:02', 'Ice machine is broken', '', ''),
      ('Michael Arthur', 'Q-Bar', '', 'Initiated', 'Urgent', '2024-01-05 00:10:02', 'Lane 5 has missing pin', '', ''),
      ('Ben Davis', 'Cosmic', '', 'Complete', '     ', '2024-01-04 00:10:02', 'Pac-Man controller doesnt turn', '', ''), 
      ('Warren Kerr', 'Cafe', '', 'Complete', '     ', '2024-01-03 00:10:02', 'Soda machine doesnt dispense drink', '', ''),
   ]


data_to_insert_Deps = [
    ('Boardwalk',),
    ('Bowl',),
    ('Pizza',),
    ('Cafe',),
    ('Billiards',),
    ('Q-Bar',),
    ('Cosmic',),
]


root_psw = auth.hash_password('BackupStuff')
Users_psw = auth.hash_password('123')
User_Reg = [('Root', root_psw),
            ('Users',Users_psw)]


# SQL query for insertion
insert_query = "INSERT INTO WO (`name`, `department`, `signature`, ticket_status, `urgent_status`, `date`, `notes`, `tech_notes`, `complete_date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

# insert into users
insert_query3 = "INSERT INTO users VALUES (%s, %s)"

insert_query4 = "INSERT INTO departments VALUES (%s)"

# Insert data into the database
try:
    cursor.executemany(insert_query, data_to_insert)
    #cursor.executemany(insert_query2, data_to_insert_His)
    cursor.executemany(insert_query3, User_Reg)
    cursor.executemany(insert_query4, data_to_insert_Deps)
    conn.commit()
    print(cursor.rowcount, "record(s) inserted successfully.")
except mysql.connector.Error as err:
    print("Error: {}".format(err))
    conn.rollback()
finally:
    cursor.close()
    conn.close()

#Closing the connection
conn.close()