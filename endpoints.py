import psycopg2
import re
from flask import Flask, request, jsonify
from psycopg2 import errors

from users import user

app = Flask(__name__)


@app.route('/users', methods=['POST'])
def insert_user():

    request_data = request.get_json()
    user_update = request_data.get('update', None)  # returns json value if exists, else returns None
    user_old_email = request_data.get('user_old_email', None)  # returns json value if exists, else returns None

    if user_update is None or type(user_update) is not bool:
        return jsonify({'failed': 'Please provide an update: true / false row in your json.'})

    DB = user()

    if not DB.check_regex(request_data['user_email']):  # if check_regex return False
        DB.postgres.close_postgres_connection()
        return jsonify({'failed': 'Unable to create user due to invalid email format'})

    new_user = {
        'user_email': request_data.get('user_email', None),
        'first_name': request_data.get('first_name', None),
        'last_name': request_data.get('last_name', None),
        'user_password': request_data.get('user_password', None),
        'user_role_id': request_data.get('user_role_id', None)
    }
    # check if client did not provide a required row. If a key has a None value return request for required row
    for name, val in new_user.items():
        if val is None:
            DB.postgres.close_postgres_connection()
            return jsonify(missing_value=name)

    try:
        if user_update:  # if 'update' is true
            if user_old_email is None:
                return jsonify({'failed': 'Please provide valid values for this update functionality, including a '
                                          '"user_old_email": row, empty "" or not depending on type of update'})
            elif user_old_email:
                if not DB.check_regex(request_data['user_old_email']):
                    return jsonify({'failed': 'Unable to create user due to invalid user_old_email'})
                print("Also change the email to a new email.")
                if DB.update_user(new_user.values(), old_email=request_data['user_old_email']):
                    new_user['user_new_email'] = new_user.pop('user_email')
                    return jsonify(new_user)
                else:
                    return jsonify({'failed': 'Something went wrong. User could not be updated in PostgreSQL'})
            elif not user_old_email:
                print("No require to change the email to a new email.")
                if DB.update_user(new_user.values()):  # if user successfully updated return user
                    return jsonify(new_user)
                else:
                    return jsonify({'failed': 'Something went wrong. User could not be updated in PostgreSQL'})
            else:  # pe asta il las asa just in case, desi cred ca am acoperit toate variantele prin cele 3 conditii
                return jsonify({'failed': 'error occurred, please check documentation for this http request'})

        elif not user_update:  # if 'update' is false
            # before creating a new user check if users table and user_roles table already exist. If not, create tables.
            if not DB.count_rows('users') and not DB.count_rows('user_roles'):  # if both tables do not exist
                if DB.postgres.check_user_roles() and DB.postgres.check_users():  # if both tables could be created
                    if DB.postgres.create_user_roles():  # if admin and viewer could be added
                        print("user_roles table up and running - admin and viewer columns inserted successfully into table")
                        print("users table up and running!")
                    else:
                        return jsonify({'failed': 'admin and viewer could not be added in user_roles table'})
                elif not DB.postgres.check_user_roles():
                    return jsonify({'failed': 'user_roles table could not be created in PostgreSQL'})
                elif not DB.postgres.check_users():
                    return jsonify({'failed': 'users table could not be created in PostgreSQL'})
                else:
                    return jsonify({'failed': 'none of tables could be created in PostgreSQL'})
            elif DB.count_rows('user_roles') and not DB.count_rows('users'):  # if user_roles exists but users does not
                if not DB.postgres.check_users():  # if users could not be created
                    return jsonify({'failed': 'users table could not be created in PostgreSQL'})
                else:
                    print("users table up and running.")
            elif DB.count_rows('user_roles') and DB.count_rows('users'):  # if both table exists check if admin and viewer exist
                if DB.postgres.create_user_roles():  # if admin and viewer could be added or already existed
                    print("admin and viewer columns exist in user_roles table")
                else:
                    return jsonify({'failed': 'user_roles table exists but admin and viewer could not be added in user_roles table'})
            # no need to test the case when users table exists and user_roles does not because it can't be possible
            # because of the foreign key constraint
            else:  # just for testing
                print("Both table existed and all went good")

            new_user_data_to_tuple = [tuple(new_user.values())]
            if DB.create_user(new_user_data_to_tuple):  # if user successfully created return user
                return jsonify(new_user)
            else:
                return jsonify({'failed': 'Something went wrong. User could not be created in PostgreSQL'})

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
        DB = user()

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
        DB = user()

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
    DB = user()

    request_data = request.get_json()
    user_email = request_data.get('user_email', None)  # returns json value if exists, else returns None
    user_password = request_data.get('user_password', None)  # returns json value if exists, else returns None
    if user_email is None:
        return jsonify(missing_value='user_email')
    elif user_password is None:
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