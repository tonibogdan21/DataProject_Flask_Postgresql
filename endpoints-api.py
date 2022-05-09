from flask import Flask, request
import psycopg2
from DB_PostgreSQL import Postgres
from users import user

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def insert_user():
    pass
    # global DB
    #
    # try:
    #
    #     DB = user()
    #     DB.connect_to_postgres()
    # except (Exception, psycopg2.Error) as error:
    #     print("Error - operation failed: {}".format(error))
    # finally:
    #     DB.close_postgres_connection()


@app.route('/users/<string:name>')
def get_user(name):
    request_data = request.get_json()


    if request_data[name] in request_data:
        return request_data[name]

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()