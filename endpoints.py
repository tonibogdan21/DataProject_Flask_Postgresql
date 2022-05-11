from flask import Flask, request, jsonify
import psycopg2
from users import user

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def insert_user():
    global DB
    try:
        DB = user()
        DB.connect_to_postgres()

        request_data = request.get_json()
        new_user = {
            'user_email': request_data['user_email'],
            'first_name': request_data['first_name'],
            'last_name': request_data['last_name'],
            'user_password': request_data['user_password'],
            'user_role_id': request_data['user_role_id']
        }
        new_user_data_to_tuple = [tuple(new_user.values())]
        DB.create_user(new_user_data_to_tuple)

        return jsonify(new_user)

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        DB.close_postgres_connection()

@app.route('/users/<string:email>')
def get_user(email):
    global DB
    try:
        DB = user()
        DB.connect_to_postgres()
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
        DB.close_postgres_connection()

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
