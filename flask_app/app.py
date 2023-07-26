from flask import request, jsonify, json
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt
import re
from sqlalchemy.exc import SQLAlchemyError

from logging_config import configure_logging
from database.models import User, OnlineUser
from database.config import app, db

# Load logging configuration
configure_logging()


# Endpoint for login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        app.logger.info("invalid json data entry at login")
        return jsonify({"error": "Invalid data. 'username' and 'password' fields are required."}), 400

    username = data['username']

    try:
        user = User.query.filter_by(username=username).first()

        # Check if the provided username exists and the password is correct
        if user:
            if verify_password(data['password'], user.password):
                # Update user status and login time in online_users table
                login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                online_user = OnlineUser(id=user.id, username=user.username,
                                         ipaddress=request.remote_addr, login_time=login_time)
                db.session.add(online_user)
                db.session.commit()

                app.logger.info("Login successful for user_id %s", user.id)
                return jsonify({"message": "Login successful!"}), 200
            else:
                app.logger.info("invalid password at login, user id: %s", user.id)
                return jsonify({"error": "Invalid password. Please check your password."}), 401
        else:
            app.logger.info("invalid username at login")
            return jsonify({"error": "Invalid credentials. Please check your username and password."}), 401

    except SQLAlchemyError as e:
        app.logger.error("login: %s", e)
        db.session.rollback()  # Rollback changes in case of error
        return jsonify({"error": "An error occurred during login."}), 500


# Endpoint for logout
@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    if not data or 'username' not in data:
        app.logger.info("invalid json data entry at logout")
        return jsonify({"error": "Invalid data. 'username' field is required."}), 400

    username = data['username']

    try:

        online_user = OnlineUser.query.filter_by(username=username).first()

        if online_user:
            db.session.delete(online_user)
            db.session.commit()

            app.logger.info("Logout successful for user_id %s", online_user.id)
            return jsonify({"message": "User logged out successfully."}), 200
        else:
            app.logger.info("invalid username at logout")
            return jsonify({"error": "No user with this username."}), 401

    except SQLAlchemyError as e:
        app.logger.error("logout: %s", e)
        return jsonify({"error": "An error occurred during login."}), 500


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

    try:
        # Check if the email or username is already registered
        existing_user_email = User.query.filter_by(email=email).first()
        existing_user_username = User.query.filter_by(username=username).first()

        if existing_user_email:
            app.logger.info("invalid email entry at user registration - already taken")
            return jsonify({"error": "This email is already registered."}), 400
        elif existing_user_username:
            app.logger.info("invalid username entry at user registration - already taken")
            return jsonify({"error": "This username is already registered."}), 400
        else:
            new_user = User(
                username=username,
                first_name=firstname,
                middle_name=middlename,
                last_name=lastname,
                birthdate=birthdate,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            app.logger.info("Registration successful")
            return jsonify({"message": "User registered successfully."}), 200

    except SQLAlchemyError as e:
        app.logger.error("create_user: %s", e)
        return jsonify({"error": "An error occurred while creating user."}), 500


# Endpoint for deleting a user by ID
@app.route('/user/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        is_online = OnlineUser.query.filter_by(id=user_id).first()

        if is_online:
            app.logger.warning("Trying to delete online user with id %s", user_id)
            return jsonify({"error": "The user is online, try when user is offline."}), 400

        if user:
            db.session.delete(user)
            db.session.commit()

            app.logger.info("Deletion successful for user_id %s", user_id)
            return jsonify({"message": f"User with id {user_id} deleted successfully."}), 200
        else:
            app.logger.info("invalid user id at user deletion")
            return jsonify({"error": f"No user with id {user_id} found."}), 400

    except Exception as e:
        app.logger.error("delete: %s", e)
        return jsonify({"error": "An error occurred while deleting user."}), 500


# Endpoint for updating a user by ID
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data or not any(field in data for field in ['username', 'firstname', 'lastname', 'birthdate', 'email']):
        app.logger.info("invalid data entry at user update")
        return jsonify({"error": "Invalid data. At least one of 'username', "
                        "'firstname', 'lastname', 'birthdate', 'email' fields are required."}), 400

    try:
        user = User.query.filter_by(id=user_id).first()
        is_online = OnlineUser.query.filter_by(id=user_id).first()

        if not user:
            app.logger.info("invalid user id at user update")
            return jsonify({"error": f"No user with id {user_id} found."}), 400

        if is_online:
            app.logger.warning("Trying to update online user with id %s", user_id)
            return jsonify({"error": "The user is online, try when user is offline."}), 400

        # TODO: check if new username or email is not taken

        # Update the user data with the new values if provided
        if 'username' in data:
            user.username = data['username']
        if 'firstname' in data:
            user.first_name = data['firstname']
        if 'lastname' in data:
            user.last_name = data['lastname']
        if 'birthdate' in data and is_birthdate_valid(data['birthdate']):
            user.birthdate = data['birthdate']
        if 'email' in data and is_email_valid(data['email']):
            user.email = data['email']

        # Commit the changes
        db.session.commit()

        app.logger.info("Update successful for user_id %s", user_id)
        return jsonify({"message": f"User with id {user_id} updated successfully."}), 200

    except Exception as e:
        app.logger.error("update_user %s", e)
        return jsonify({"error": "An error occurred during user update."}), 500


# Endpoint for listing all users
@app.route('/user/list', methods=['GET'])
def list_users():
    try:
        users = User.query.order_by(User.id).all()

        # Convert the users to a list of dictionaries
        users_data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'middle_name': user.middle_name,
                'last_name': user.last_name,
                'birthdate': str(user.birthdate),  # Convert date to string for JSON serialization
            }
            for user in users
        ]

        # Use json.dumps with sort_keys=False to preserve order
        json_response = json.dumps(users_data, indent=2, sort_keys=False)

        # Set the Content-Type header to 'application/json'
        response = app.response_class(
            response=json_response,
            status=200,
            mimetype='application/json'
        )

        app.logger.info("list_users successful")
        return response

    except SQLAlchemyError as e:
        app.logger.error("list_users: %s", e)
        return jsonify({"error": "An error occurred."}), 500


# Endpoint for getting online users
@app.route('/onlineusers', methods=['GET'])
def get_online_users():
    try:
        online_users = OnlineUser.query.all()

        # Convert the users to a list of dictionaries
        users_data = [
            {
                'id': user.id,
                'username': user.username,
                'ipaddress': user.ipaddress,
                'login_time': user.login_time,
            }
            for user in online_users
        ]

        # Use json.dumps with sort_keys=False to preserve order
        json_response = json.dumps(users_data, indent=2, sort_keys=False)

        # Set the Content-Type header to 'application/json'
        response = app.response_class(
            response=json_response,
            status=200,
            mimetype='application/json'
        )

        app.logger.info("get_online_users successful")
        return response

    except SQLAlchemyError as e:
        app.logger.error("get_online_users: %s", e)
        return jsonify({"error": "An error occurred."}), 500


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


def check_logout_users():
    try:
        online_users = OnlineUser.query.all()
        current_time = datetime.now()

        for user in online_users:
            login_time = user.login_time
            duration = current_time - login_time

            # Set the maximum allowed online time here (e.g., 30 minutes)
            max_online_time = timedelta(minutes=30)

            if duration > max_online_time:
                db.session.delete(user)
                db.session.commit()
                app.logger.info("User with id %s logged out due to session timeout.", user.id)

    except SQLAlchemyError as e:
        app.logger.error("check_logout_users: %s", e)
        db.session.rollback()


if __name__ == '__main__':
    app.run(debug=True)
