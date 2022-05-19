import psycopg2
from dotenv import dotenv_values


class Postgres:
    config = dotenv_values()  # this returns a dict with key-value pairs from .env file

    def __init__(self, host=config['host'], database=config['database'], user=config['user'],
                 password=config['password']):
        self.connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        self.cursor = self.connection.cursor()
        print('PostgreSQL open')

    def close_postgres_connection(self):
        # closing database connection
        self.cursor.close()
        self.connection.close()
        print("PostgreSQL connection is closed")

    # Verify if the user_roles table exists - if not then create table, also check if the 2 roles exist - if not
    # create the 2 roles
    def create_user_roles(self):
        # check if the table exists
        sql_create_table_user_roles = """CREATE TABLE IF NOT EXISTS user_roles (
                                            role_id INT,
                                            role_description VARCHAR(50) NOT NULL,
                                            PRIMARY KEY (role_id)
                                      )
                                      """
        self.cursor.execute(sql_create_table_user_roles)
        self.connection.commit()

        # add the 2 roles if they not exist
        sql_number_roles = """SELECT COUNT(1) FROM user_roles"""
        self.cursor.execute(sql_number_roles)
        result = self.cursor.fetchone()
        # trebuie modificata aici pt error handling
        if result[0] == 0:
            roles = [(1, 'admin'), (2, 'viewer')]
            sql_insert_two_roles = """ INSERT INTO user_roles (role_id, role_description)
                                        VALUES (%s,%s) """
            self.cursor.executemany(sql_insert_two_roles, roles)
            self.connection.commit()
            print("User roles - admin and viewer - inserted successfully into user_roles table")
        print("user_roles table up and running!")

    # Verify if the users table exists, if not then create table
    def create_users(self):
        sql_create_table_users = """CREATE TABLE IF NOT EXISTS users (
                        user_id INT GENERATED ALWAYS AS IDENTITY,
                        user_email VARCHAR(50), 
                        user_first_name VARCHAR(30) NOT NULL,
                        user_last_name VARCHAR(30) NOT NULL,
                        user_password VARCHAR(150) NOT NULL,
                        user_role_id INT REFERENCES user_roles(role_id) ON DELETE SET NULL,
                        PRIMARY KEY (user_id, user_email)
            )
            """
        self.cursor.execute(sql_create_table_users)
        self.connection.commit()
        print("users table up and running!")


# DB = Postgres()
#
# DB.create_user_roles()
# DB.create_users()
# DB.close_postgres_connection()