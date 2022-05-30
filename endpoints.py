import psycopg2
from flask import Flask, request, jsonify
from psycopg2 import errors

from users import User
from users import create_user_prerequisites, check_regex

app = Flask(__name__)


@app.route('/users', methods=['POST'])
def insert_user():
    DB = User()
    global new_user

    request_data = request.get_json()
    result = create_user_prerequisites(request_data)  # pass data from Postman to function

    if result is None:  # result is None when 'update' is not passed as true or false in Postman or is None
        return jsonify({'failed': 'Please provide an update: true / false row in your json.'})

    if not check_regex(request_data['user_email']):  # if check_regex return False
        DB.postgres.close_postgres_connection()
        return jsonify({'failed': 'Unable to create user due to invalid email format'})

    if result[0]:  # if result[0] was True it means all required values were found in json
        new_user = result[1]

    if not result[0]:  # if result[0] was False it means there was a None value in json
        DB.postgres.close_postgres_connection()
        return jsonify(missing_value=result[1])

    try:
        if request_data['update']:  # if 'update' is true
            update_result = DB.postman_update_user_by_email(new_user, request_data['user_old_email'])

            if update_result is None:
                return jsonify({'failed': 'Please provide valid values for this update functionality, including a '
                                          '"user_old_email" row, empty "" or not depending on type of update'})
            elif update_result == "invalidEmail":
                return jsonify({'failed': 'Unable to create user due to invalid user_old_email'})
            elif update_result == "userUpdateFail":
                return jsonify({'failed': 'Something went wrong. User could not be updated in PostgreSQL'})
            elif update_result == "generalFail":
                return jsonify({'failed': 'error occurred, please check documentation for this http request'})
            else:
                return jsonify(update_result)

        elif not request_data['update']:  # if 'update' is false
            add_user = DB.add_user(new_user)

            if add_user == "userRolesTableAddFailed":
                return jsonify({'failed': 'admin and viewer could not be added in user_roles table'})
            elif add_user == "userRolesCreationFailed":
                return jsonify({'failed': 'user_roles table could not be created in PostgreSQL'})
            elif add_user == "usersCreationFailed":
                return jsonify({'failed': 'users table could not be created in PostgreSQL'})
            elif add_user == "bothTablesFailed":
                return jsonify({'failed': 'none of tables could be created in PostgreSQL'})
            elif add_user == "userRolesExistsButFailed":
                return jsonify({'failed': 'user_roles table exists but admin and viewer could not be added in user_roles table'})
            elif add_user == "generalFail":
                return jsonify({'failed': 'Something went wrong. User could not be created in PostgreSQL'})
            else:
                return jsonify(add_user)

        else:  # pe asta il las asa just in case, desi cred ca am acoperit toate variantele prin cele 4 conditii
            return jsonify({'failed': 'Please provide a http request with all the required values of body json.'})

    except errors.UniqueViolation:
        return jsonify({'failed': 'A user with this email already exists in PostgreSQL.'})
    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        DB.postgres.close_postgres_connection()


@app.route('/users/<string:email>')
def get_user(email):
    global DB

    try:
        DB = User()

        email_exists = DB.get_user_data_by_email([email])
        if not email_exists:
            return jsonify({'error': 'user email not found, check spelling or try another email'})
        else:
            return jsonify(email_exists)

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        if DB.postgres.connection:
            DB.postgres.close_postgres_connection()


@app.route('/users/<string:email>', methods=['DELETE'])
def delete_user(email):
    global DB

    try:
        DB = User()

        if DB.track_exists([email]):
            if DB.delete_user([email]):
                print(f"The user with email: {email} deleted successfully")
                return jsonify({'success': 'user deleted'})
            else:
                return jsonify({'failed': 'unable to delete the user from PostgreSQL.'})
        else:
            return jsonify({'failed': 'no user in DB with this email'})

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        if DB.postgres.connection:
            DB.postgres.close_postgres_connection()


@app.route('/login', methods=['GET', 'POST'])
def login():
    DB = User()

    request_data = request.get_json()
    if request_data.get('user_email', None) is None:
        return jsonify(missing_value='user_email')
    elif request_data.get('user_password', None) is None:
        return jsonify(missing_value='user_password')

    try:
        # check the match between hashed pw saved in DB and pw introduced by user in Postman
        match = DB.check_match([request_data['user_email']], request_data['user_password'].encode('utf-8'))

        if not match:
            return jsonify({'error': 'invalid user email / password combo'})
        else:
            return jsonify(match)

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        DB.postgres.close_postgres_connection()


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()
