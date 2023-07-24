from flask import Flask, request, jsonify
import datetime
import psycopg2 as db
import os

app = Flask(__name__)


def get_db_conn():
    conn = db.connect(host="localhost",
                      dbname="flask_db",
                      user=os.environ['DB_USERNAME'],
                      password=os.environ['DB_PASSWORD'],
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

    user = find_user_by_username(username)

    # Check if the provided username exists and the password is correct
    if user:
        if user["password"] == password:
            user['is_online'] = True
            user['last_login'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Invalid password. Please check your password."}), 401
    else:
        return jsonify({"error": "Invalid credentials. Please check your username and password."}), 401


# Endpoint for logout
@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Invalid data. 'username' field is required."}), 400

    username = data['username']
    user = find_user_by_username(username)
    if user:
        user['is_online'] = False
        return jsonify({"message": "Logout successful!"}), 200
    else:
        return jsonify({"error": "User not found."}), 404


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
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    users.remove(user)
    return jsonify({"message": "User deleted successfully."}), 200


# Endpoint for updating a user by ID
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data. Please provide updated user information."}), 400

    user['username'] = data.get('username', user['username'])
    user['email'] = data.get('email', user['email'])
    user['is_online'] = data.get('is_online', user['is_online'])

    return jsonify(user), 200


# Endpoint for getting online users
@app.route('/onlineusers', methods=['GET'])
def get_online_users():
    online_users = []
    for user in users:
        if user['is_online']:
            online_user_info = {
                "username": user['username'],
                "ipaddress": request.remote_addr,
                "last_login": user['last_login']
            }
            online_users.append(online_user_info)
    return jsonify(online_users)


# Helper function to find a user by ID
def find_user_by_id(user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def find_user_by_username(username):
    for user in users:
        if user["username"] == username:
            return user
    return None


if __name__ == '__main__':
    app.run(debug=True)
