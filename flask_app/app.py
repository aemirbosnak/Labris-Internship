from flask import Flask, request, jsonify
import datetime
import psycopg2 as db
import psycopg2.extras

app = Flask(__name__)


def get_db_conn():
    conn = db.connect(host="localhost",
                      dbname="flask_db",
                      user="flask",
                      password="flask123",
                      port="5432")
    return conn


# Endpoint for login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Invalid data. 'username' and 'password' fields are required."}), 400

    username = data['username']
    password = data['password']

    # Database connection
    conn = get_db_conn()
    if conn is None:
        return jsonify({"error": "Could not connect to the database."}), 500
    cursor = conn.cursor(cursor_factory=db.extras.DictCursor)

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()

        # Check if the provided username exists and the password is correct
        if user:
            if user['password'] == password:
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
    if conn is None:
        return jsonify({"error": "Could not connect to the database."}), 500
    cursor = conn.cursor(cursor_factory=db.extras.DictCursor)

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

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(users)


# Endpoint for creating a new user
@app.route('/user/create', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'username' not in data or 'firstname' not in data or 'lastname' not in data or \
            'birthdate' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Invalid data. 'username', 'firstname', 'lastname', 'birthdate', "
                                 "'email', and 'password' fields are required."}), 400

    username = data['username']
    firstname = data['firstname']
    middlename = data.get('middlename', '')  # Optional field, set to empty string if not provided
    lastname = data['lastname']
    birthdate = data['birthdate']
    email = data['email']
    password = data['password']

    # Check if the username already exists
    if find_user_by_username(username):
        return jsonify({"error": "Username already exists. Please choose a different username."}), 409

    # Generate a unique user ID (for demo purposes, not recommended for production)
    user_id = len(users) + 1

    # Create the new user dictionary
    new_user = {
        "id": user_id,
        "username": username,
        "firstname": firstname,
        "middlename": middlename,
        "lastname": lastname,
        "birthdate": birthdate,
        "email": email,
        "password": password,
        "is_online": False,
        "last_login": None
    }

    users.append(new_user)
    return jsonify(new_user), 201


# Endpoint for deleting a user by ID
@app.route('/user/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return 0


# Endpoint for updating a user by ID
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return 0


# Endpoint for getting online users
@app.route('/onlineusers', methods=['GET'])
def get_online_users():
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute('SELECT * FROM online_users')
    online_users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(online_users)


if __name__ == '__main__':
    app.run(debug=True)
