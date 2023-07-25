from flask import Flask, request, jsonify
import datetime
import psycopg2 as db
import psycopg2.extras
from passlib.hash import sha256_crypt
import re

app = Flask(__name__)

# TODO: implement activity logging
# TODO: serve application with uwsgi and nginx
# TODO: use sqlalchemy


def get_db_conn():
    conn = db.connect(host="localhost",
                      dbname="flask_db",
                      user="flask",
                      password="flask123",
                      port="5432")
    if conn is None:
        return jsonify({"error": "Could not connect to the database."}), 500

    return conn


def is_password_valid(password):
    # password complexity: at least one from [A-Za-z0-9] and min 8 characters
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z0-9]{8,}$'
    return bool(re.match(pattern, password))


def is_email_valid(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def encrypt_password(password):
    # passlib library hash function uses salt when hashing
    return sha256_crypt.hash(password)


def verify_password(input_password, stored_password):
    return sha256_crypt.verify(input_password, stored_password)


# Endpoint for login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
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

                return jsonify({"message": "Login successful!"}), 200
            else:
                return jsonify({"error": "Invalid password. Please check your password."}), 401
        else:
            return jsonify({"error": "Invalid credentials. Please check your username and password."}), 401

    except Exception as e:
        print("Error during login:", e)
        return jsonify({"error": "An error occurred during login."}), 500

    finally:
        conn.close()


# Endpoint for logout
@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Invalid data. 'username' field is required."}), 400

    username = data['username']

    # Database connection
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                "DELETE FROM online_users WHERE username = %s;", (username,))
            conn.commit()

            return jsonify({"message": "User logged out successfully."}), 200
        else:
            return jsonify({"error": "No user with this username."}), 401

    except Exception as e:
        print("Error during login:", e)
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
        print("Error listing users:", e)
        return jsonify({"error": "An error occurred."}), 500

    finally:
        conn.close()


# Endpoint for creating a new user
@app.route('/user/create', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'username' not in data or 'firstname' not in data \
            or 'lastname' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Invalid data. 'username', 'firstname', 'lastname', 'birthdate', "
                                 "'email', and 'password' fields are required."}), 400

    username = data['username']
    firstname = data['firstname']
    middlename = data.get('middlename', None)  # Optional field, set to empty string if not provided
    lastname = data['lastname']
    birthdate = data.get('birthdate', None)  # Optional

    if not is_email_valid(data['email']):
        return jsonify({"error": "Enter a valid email address."}), 400
    email = data['email']

    if not is_password_valid(data['password']):
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
            return jsonify({"error": "This email is already registered."}), 400
        elif accountExistWithSameUsername:
            return jsonify({"error": "This username is already registered."}), 400
        else:
            cur.execute('INSERT INTO users (username, first_name, middle_name, last_name, birthdate, email, password) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (username, firstname, middlename, lastname, birthdate, email, password))
            conn.commit()
            return jsonify({"message": "User registered successfully."}), 200

    except Exception as e:
        print("Error creating user:", e)
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
            return jsonify({"message": f"User with id {user_id} deleted successfully."}), 200
        else:
            return jsonify({"error": f"No user with id {user_id} found."}), 400

    except Exception as e:
        print("Error deleting user:", e)
        return jsonify({"error": "An error occurred while deleting user."}), 500

    finally:
        cur.close()
        conn.close()


# Endpoint for updating a user by ID
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data or not any(field in data for field in ['username', 'firstname', 'lastname', 'birthdate', 'email']):
        return jsonify({"error": "Invalid data. At least one of 'username', "
                        "'firstname', 'lastname', 'birthdate', 'email' fields are required."}), 400

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=db.extras.DictCursor)

    try:
        # Check if the user with the given user_id exists
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
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
        new_birthdate = data.get('birthdate', existing_birthdate)
        new_email = data.get('email', existing_email)

        # Execute the update query
        cur.execute(
            "UPDATE users SET username=%s, first_name=%s, last_name=%s, birthdate=%s, email=%s WHERE id=%s;",
            (new_username, new_firstname, new_lastname, new_birthdate, new_email, user_id)
        )
        conn.commit()

        return jsonify({"message": f"User with id {user_id} updated successfully."}), 200

    except Exception as e:
        print("Error updating user:", e)
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
        print("Error listing online users:", e)
        return jsonify({"error": "An error occurred."}), 500

    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
