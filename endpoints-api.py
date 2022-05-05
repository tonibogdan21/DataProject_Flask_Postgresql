from flask import Flask

app = Flask(__name__)

# Create a user
@app.route('/users', methods=['POST'])
def insert_user():
    pass

# Retrieve a user
@app.route('/users/<string:name>')
def get_user(name):
    pass