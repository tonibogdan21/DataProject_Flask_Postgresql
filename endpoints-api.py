from flask import Flask, request, jsonify
import psycopg2
from users import user

app = Flask(__name__)

users_list = []

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
        users_list.append(new_user)
        new_user_data_to_tuple = [tuple(new_user.values())]
        DB.create_user(new_user_data_to_tuple)

        return jsonify({'success': 'user successfully created'})

    except (Exception, psycopg2.Error) as error:
        print("Error - database connection failed: {}".format(error))
        return jsonify({'failed': 'Unable to create user due to server error'})
    finally:
        DB.close_postgres_connection()

@app.route('/users/<string:email>')
def get_user(email):
    for user_data in users_list:
        if user_data['user_email'] == email:
            #aici improvizez putin si copiez informatiile in alt dict, sterg password si returnez noul dict ce nu contine password
            user_data_without_password = user_data
            user_data_without_password.pop('user_password')
            return jsonify(user_data_without_password)
    return jsonify({'error': 'user email not found'})

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
