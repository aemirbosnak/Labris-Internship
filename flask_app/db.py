import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="flask_db",
    user="flask",
    password="flask123",
    port="5432"
)

cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS online_users CASCADE;')
cursor.execute('DROP TABLE IF EXISTS users CASCADE;')

cursor.execute('CREATE TABLE users ('
               'id serial PRIMARY KEY ,'
               'username varchar (50) UNIQUE NOT NULL,'
               'first_name varchar (50) NOT NULL,'
               'middle_name varchar (50),'
               'last_name varchar (50) NOT NULL,'
               'birthdate date,'
               'email varchar (100) UNIQUE,'
               'password varchar (50) NOT NULL);'
               )

cursor.execute('CREATE TABLE online_users ('
               'user_id integer PRIMARY KEY REFERENCES users(id),'
               'username varchar (50) REFERENCES users(username),'
               'ipaddress inet NOT NULL,'
               'login_time timestamp NOT NULL);'
               )

cursor.execute('INSERT INTO users (username, first_name, last_name, email, password)'
               'VALUES (%s, %s, %s, %s, %s)',
                ('oppie',
                 'Robert',
                 'Oppenheimer',
                 'oppie@town.com',
                 'BuildItFast')
                )

cursor.execute('INSERT INTO users (username, first_name, last_name, email, password)'
               'VALUES (%s, %s, %s, %s, %s)',
                ('einstein',
                 'Albert',
                 'Einstein',
                 'albert@town.com',
                 'MyHat')
                )

conn.commit()

cursor.close()
conn.close()