import psycopg2
import re
import bcrypt
from flask import Flask, request, jsonify

from users import user

app = Flask(__name__)


@app.route('/users', methods=['POST'])
def insert_user():
    global DB

    # validate user email with regex
    request_data = request.get_json()
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, request_data['user_email']):
        return jsonify({'failed': 'Unable to create user due to invalid email format'})

    try:
        DB = user()
        new_user = {
            'user_email': request_data['user_email'],
            'first_name': request_data['first_name'],
            'last_name': request_data['last_name'],
            'user_password': request_data['user_password'],
            'user_role_id': request_data['user_role_id']
        }
        user_update = request_data.get('update', None)  # returns json value if exists, else returns None
        user_old_password = request_data.get('user_old_email', None)  # returns json value if exists, else returns None

        if user_update is None:
            return jsonify({'failed': 'Please provide an "update": "True/False" row in your json.'})

        elif request_data['update'] == "True":
            if user_old_password is None:
                return jsonify({'failed': 'Please provide valid values for this update functionality, including a '
                                          '"user_old_email": row, empty "" or not depending on type of update'})
            elif request_data['user_old_email'] is "":
                print("No require to change the email to a new email.")
                DB.update_user(new_user.values())
            elif request_data['user_old_email'] is not "":
                print("Also change the email to a new email.")
                if not re.search(regex, request_data['user_old_email']):
                    return jsonify({'failed': 'Unable to create user due to invalid user_old_email'})
                DB.update_user(new_user.values(), old_email=request_data['user_old_email'])
            else:
                return jsonify({'failed': 'error occurred, please check documentation for this http request'})

        elif request_data['update'] == "False":
            # before creating a new user check if users table and user_roles table already exist. If not, create tables.
            if not DB.count_rows():
                DB.postgres.create_user_roles()
                DB.postgres.create_users()
            new_user_data_to_tuple = [tuple(new_user.values())]
            DB.create_user(new_user_data_to_tuple)
        else:
            return jsonify({'failed': 'Please provide a http request with all the required values of body json.'})

        return jsonify(new_user)

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        if DB.postgres.connection:
            DB.postgres.close_postgres_connection()


@app.route('/users/<string:email>')
def get_user(email):
    global DB

    try:
        DB = user()

        email_exists = DB.get_user_by_email([email])
        if email_exists is None:
            return jsonify({'error': 'user email not found, check spelling or try another email'})
        else:
            existing_user = {
                'user_email': email_exists[1],
                'first_name': email_exists[2],
                'last_name': email_exists[3],
                'user_role_id': email_exists[5]
            }
            return jsonify(existing_user)

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
            DB.delete_user([email])
            return jsonify({'success': 'user deleted'})
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
    request_data = request.get_json()
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, request_data['user_email']):
        return jsonify({'failed': 'Unable to login due to invalid email format'})

    global DB

    try:
        DB = user()
        email = request_data['user_email']
        user_password = DB.get_user_password([email])

        if user_password is False:
            return jsonify({'error': 'no user with this email in database'})

        else:
            input_password = request_data['user_password'].encode('utf-8')
            if bcrypt.checkpw(input_password, user_password):
                return jsonify({'success': 'login successfully done'})
            else:
                return jsonify({'failed': 'login could not happen due to incorrect password'})

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        if DB.postgres.connection:
            DB.postgres.close_postgres_connection()


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()
