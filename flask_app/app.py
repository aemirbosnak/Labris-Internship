from flask import Flask, request, jsonify
import datetime
import psycopg2 as db
import psycopg2.extras
from passlib.hash import sha256_crypt
import re
from logging.config import dictConfig

# Logging configuration and formatting (needs to be done before app initialization)
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'flask.log',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
})

app = Flask(__name__)

# TODO: implement activity logging
# TODO: serve application with uwsgi and nginx
# TODO: use sqlalchemy

# MAYBE TODO: change login system to flask sessions
# MAYBE TODO: custom error messages for incorrect api request methods
# MAYBE TODO: randomized user ids


def get_db_conn():
    try:
        conn = db.connect(host="localhost",
                          dbname="flask_db",
                          user="flask",
                          password="flask123",
                          port="5432")
        return conn

    except Exception as e:
        print("Error - database connection:", e)
        return jsonify({"error": "Could not connect to the database."}), 500


def is_password_valid(password):
    try:
        # password complexity: at least one from [A-Za-z0-9] and min 8 characters
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z0-9]{8,}$'
        return bool(re.match(pattern, password))

    except Exception as e:
        app.logger.error("password validation: %s", e)
        return jsonify({"error": "An error occurred."}), 500


def is_email_valid(email):
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    except Exception as e:
        app.logger.error("email validation: %s", e)
        return jsonify({"error": "An error occurred."}), 500


def is_birthdate_valid(birthdate):
    if not birthdate:
        return True

    date_format_european = "%d-%m-%Y"
    date_format_american = "%m-%d-%Y"

    try:
        res = bool(datetime.strptime(birthdate, date_format_european)) or \
              bool(datetime.strptime(birthdate, date_format_american))
        return res

    except Exception as e:
        app.logger.error("birthdate validation: %s", e)
        return jsonify({"error": "An error occurred."}), 500


def encrypt_password(password):
    try:
        # passlib library hash function uses salt when hashing
        return sha256_crypt.hash(password)

    except Exception as e:
        app.logger.error("password encryption: %s", e)
        return jsonify({"error": "An error occurred."}), 500


def verify_password(input_password, stored_password):
    try:
        return sha256_crypt.verify(input_password, stored_password)

    except Exception as e:
        app.logger.error("password verification: %s", e)
        return jsonify({"error": "An error occurred."}), 500


# Endpoint for login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        app.logger.info("invalid json data entry at login")
        return jsonify({"error": "Invalid data. 'username' and 'password' fields are required."}), 400

    username = data['username']

    # Database connection
    conn = get_db_conn()
    cursor = conn.cursor(cursor_factory=db.extras.DictCursor)

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()

        # Check if the provided username exists and the password is correct
        if user:
            if verify_password(data['password'], user['password']):
                # Update user status and login time in online_users table
                login_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO online_users (user_id, username, ipaddress, login_time) VALUES (%s, %s, %s, %s);",
                    (user['id'], user['username'], request.remote_addr, login_time))
                conn.commit()

                app.logger.info("Login successful for user_id %s", user['id'])
                return jsonify({"message": "Login successful!"}), 200
            else:
                app.logger.info("invalid password at login, user id: %s", user['id'])
                return jsonify({"error": "Invalid password. Please check your password."}), 401
        else:
            app.logger.info("invalid username at login")
            return jsonify({"error": "Invalid credentials. Please check your username and password."}), 401

    except Exception as e:
        app.logger.error("login: %s", e)
        return jsonify({"error": "An error occurred during login."}), 500

    finally:
        conn.close()


# Endpoint for logout
@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    if not data or 'username' not in data:
        app.logger.info("invalid json data entry at logout")
        return jsonify({"error": "Invalid data. 'username' field is required."}), 400

    username = data['username']

    # Database connection
    conn = get_db_conn()
    cursor = conn.cursor(cursor_factory=db.extras.DictCursor)

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                "DELETE FROM online_users WHERE username = %s;", (username,))
            conn.commit()
            app.logger.info("Logout successful for user_id %s", user['id'])
            return jsonify({"message": "User logged out successfully."}), 200
        else:
            app.logger.info("invalid username at logout")
            return jsonify({"error": "No user with this username."}), 401

    except Exception as e:
        app.logger.error("logout: %s", e)
        return jsonify({"error": "An error occurred during login."}), 500

    finally:
        conn.close()


# Endpoint for listing all users
@app.route('/user/list', methods=['GET'])
def list_users():
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()

        cur.close()
        return jsonify(users), 200

    except Exception as e:
        app.logger.error("list_users: %s", e)
        return jsonify({"error": "An error occurred."}), 500

    finally:
        conn.close()


# Endpoint for creating a new user
@app.route('/user/create', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'username' not in data or 'firstname' not in data \
            or 'lastname' not in data or 'email' not in data or 'password' not in data:
        app.logger.info("invalid json data entry at user registration")
        return jsonify({"error": "Invalid data. 'username', 'firstname', 'lastname', 'birthdate', "
                                 "'email', and 'password' fields are required."}), 400

    username = data['username']
    firstname = data['firstname']
    middlename = data.get('middlename', None)  # Optional field, set to empty string if not provided
    lastname = data['lastname']

    if not is_birthdate_valid(data.get('birthday', None)):
        app.logger.info("invalid birthdate entry at user registration")
        return jsonify({"error": "Enter a valid birthdate."}), 400
    birthdate = data.get('birthdate', None)  # Optional

    if not is_email_valid(data['email']):
        app.logger.info("invalid email entry at user registration")
        return jsonify({"error": "Enter a valid email address."}), 400
    email = data['email']

    if not is_password_valid(data['password']):
        app.logger.info("invalid password entry at user registration")
        return jsonify({"error": "Password should be longer than 8 characters and "
                                 "include at least one alphanumeric character."}), 400
    password = encrypt_password(data['password'])

    conn = get_db_conn()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM users WHERE email = %s ', (email,))
        accountExistWithSameEmail = cur.fetchone()

        cur.execute('SELECT * FROM users WHERE username = %s ', (username,))
        accountExistWithSameUsername = cur.fetchone()

        if accountExistWithSameEmail:
            app.logger.info("invalid email entry at user registration - already taken")
            return jsonify({"error": "This email is already registered."}), 400
        elif accountExistWithSameUsername:
            app.logger.info("invalid username entry at user registration - already taken")
            return jsonify({"error": "This username is already registered."}), 400
        else:
            cur.execute('INSERT INTO users (username, first_name, middle_name, last_name, birthdate, email, password) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (username, firstname, middlename, lastname, birthdate, email, password))
            conn.commit()
            app.logger.info("Registration successful")
            return jsonify({"message": "User registered successfully."}), 200

    except Exception as e:
        app.logger.error("register: %s", e)
        return jsonify({"error": "An error occurred while creating user."}), 500

    finally:
        cur.close()
        conn.close()


# Endpoint for deleting a user by ID
@app.route('/user/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if user:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            app.logger.info("Deletion successful for user_id %s", user_id)
            return jsonify({"message": f"User with id {user_id} deleted successfully."}), 200
        else:
            app.logger.info("invaid user id at user deletion")
            return jsonify({"error": f"No user with id {user_id} found."}), 400

    except Exception as e:
        app.logger.error("delete: %s", e)
        return jsonify({"error": "An error occurred while deleting user."}), 500

    finally:
        cur.close()
        conn.close()


# Endpoint for updating a user by ID
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data or not any(field in data for field in ['username', 'firstname', 'lastname', 'birthdate', 'email']):
        app.logger.info("invaid data entry at user update")
        return jsonify({"error": "Invalid data. At least one of 'username', "
                        "'firstname', 'lastname', 'birthdate', 'email' fields are required."}), 400

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=db.extras.DictCursor)

    try:
        # Check if the user with the given user_id exists
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            app.logger.info("invalid user id at user update")
            return jsonify({"error": f"No user with id {user_id} found."}), 400

        # Extract the existing data from the user row
        existing_username = user['username']
        existing_firstname = user['first_name']
        existing_lastname = user['last_name']
        existing_birthdate = user['birthdate']
        existing_email = user['email']

        # Update the user data with the new values if provided
        new_username = data.get('username', existing_username)
        new_firstname = data.get('firstname', existing_firstname)
        new_lastname = data.get('lastname', existing_lastname)

        if not is_birthdate_valid(data.get('birthdate', existing_birthdate)):
            app.logger.info("invalid birthdate entry at user update")
            return jsonify({"error": "Enter a valid birthdate."}), 400
        new_birthdate = data.get('birthdate', existing_birthdate)

        if not is_email_valid(data.get('email', existing_email)):
            app.logger.info("invalid email entry at user update")
            return jsonify({"error": "Enter a valid email."}), 400
        new_email = data.get('email', existing_email)

        # Execute the update query
        cur.execute(
            "UPDATE users SET username=%s, first_name=%s, last_name=%s, birthdate=%s, email=%s WHERE id=%s;",
            (new_username, new_firstname, new_lastname, new_birthdate, new_email, user_id)
        )
        conn.commit()
        app.logger.info("Update successful for user_id %s", user_id)
        return jsonify({"message": f"User with id {user_id} updated successfully."}), 200

    except Exception as e:
        app.logger.error("update_user %s", e)
        return jsonify({"error": "An error occurred during user update."}), 500

    finally:
        cur.close()
        conn.close()


# Endpoint for getting online users
@app.route('/onlineusers', methods=['GET'])
def get_online_users():
    conn = get_db_conn()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM online_users')
        online_users = cur.fetchall()
        return jsonify(online_users)

    except Exception as e:
        app.logger.error("get_online_users: %s", e)
        return jsonify({"error": "An error occurred."}), 500

    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
