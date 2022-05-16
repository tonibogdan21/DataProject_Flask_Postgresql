import psycopg2
import re
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
        if request_data['update'] == "True":
            if request_data['user_old_email'] is "":
                print("No require to change the email to a new email.")
                # this will take new_user_data_to_tuple and append to it the first item - email -
                # which will be used in users.py as update condition
                new_user_data_to_tuple = [tuple(new_user.values())]
                add_email_at_end = list(new_user_data_to_tuple[0])
                add_email_at_end.append(new_user['user_email'])
                new_user_data_to_tuple = [tuple(add_email_at_end)]
                DB.update_user(new_user_data_to_tuple)
            elif request_data['user_old_email'] is not "":
                print("Also change the email to a new email.")
                # this will take new_user_data_to_tuple and append to it the old email - user_old_email -
                # which will be used in users.py as update condition
                if not re.search(regex, request_data['user_old_email']):
                    return jsonify({'failed': 'Unable to create user due to invalid user_old_email'})
                new_user_data_to_tuple = [tuple(new_user.values())]
                add_email_at_end = list(new_user_data_to_tuple[0])
                add_email_at_end.append(request_data['user_old_email'])
                new_user_data_to_tuple = [tuple(add_email_at_end)]
                DB.update_user(new_user_data_to_tuple)
            else:
                return jsonify({'failed': 'Please provide valid values for this update functionality, including a '
                                          '"user_old_email": row'})

        elif request_data['update'] == "False":
            # before creating a new user check if users table and user_roles table already exist. If not, create tables.
            if not DB.count_rows():
                DB.postgres.create_user_roles()
                DB.postgres.create_users()
            new_user_data_to_tuple = [tuple(new_user.values())]
            DB.create_user(new_user_data_to_tuple)
        else:
            return jsonify({'failed': 'Please provide an "update": "True/False" row.'})

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
            return jsonify({'error': 'user email not found'})
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

    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, email):
        return jsonify({'failed': 'Unable to search for a user to delete due to invalid email format'})

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


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()
