import psycopg2
from dotenv import dotenv_values


class Postgres:
    config = dotenv_values()  # returns a dict with key-value pairs from .env file

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
    def check_user_roles(self):
        # check if the table exists
        sql_create_table_user_roles = """CREATE TABLE IF NOT EXISTS user_roles (
                                            role_id INT PRIMARY KEY,
                                            role_description VARCHAR(50) NOT NULL)
                                      """
        self.cursor.execute(sql_create_table_user_roles)
        table_created = self.cursor.rowcount
        self.connection.commit()
        if table_created == -1:  # if table could not be created return False
            return True
        return False

    def create_user_roles(self):
        # add the 2 roles if they not exist
        sql_number_roles = """SELECT COUNT(1) FROM user_roles"""
        self.cursor.execute(sql_number_roles)
        result = self.cursor.fetchone()
        if result[0] == 0:  # if user_roles table is empty
            roles = [(1, 'admin'), (2, 'viewer')]
            sql_insert_two_roles = """ INSERT INTO user_roles (role_id, role_description)
                                        VALUES (%s,%s) """
            self.cursor.executemany(sql_insert_two_roles, roles)
            row_modified = self.cursor.rowcount  # returns 2 if table affected in this situation
            self.connection.commit()
            if row_modified == 2:  # returns True if admin and viewer are successfully added
                print("user_roles was empty, but now admin an viewer added")
                return True
            else:
                print("user_roles was empty, but admin and viewer could NOT be added")
                return False
        else:
            print("user_roles was NOT empty, so no need to add admin and viewer")
            return True

    # Verify if the users table exists, if not then create table
    def check_users(self):
        sql_create_table_users = """CREATE TABLE IF NOT EXISTS users (
                        user_id INT GENERATED ALWAYS AS IDENTITY,
                        user_email VARCHAR(50) PRIMARY KEY, 
                        user_first_name VARCHAR(30) NOT NULL,
                        user_last_name VARCHAR(30) NOT NULL,
                        user_password VARCHAR(150) NOT NULL,
                        user_role_id INT REFERENCES user_roles(role_id) ON DELETE SET NULL
            )
            """
        self.cursor.execute(sql_create_table_users)
        table_created = self.cursor.rowcount  # returns -1 if table affected in this situation
        self.connection.commit()
        if table_created == -1:
            return True
        return False

    def create_csv(self):
        sql = "COPY (SELECT * FROM users) TO STDOUT WITH CSV DELIMITER ';'"
        with open("/table.csv", "w") as file:
            self.cursor.copy_expert(sql, file)


# db = Postgres()
# db.create_csv()
# db.close_postgres_connection()
