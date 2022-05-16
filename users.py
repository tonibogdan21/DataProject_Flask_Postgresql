import bcrypt

from DB_PostgreSQL import Postgres


class user:

    def __init__(self):
        self.postgres = Postgres()

    def create_user(self, users_data):
        # iterate through the list of tuples users_data to make sure we change all the
        # user_password data we receive in case of multiple inserts once
        for i in range(len(users_data)):
            # change to tuple to list so we can modify the user_password situated at index 3 and then change the list
            # back to tuple
            modified_users_data = list(users_data[i])
            password = "b'" + modified_users_data[3] + "'"
            byte_pwd = password.encode('utf-8')
            hashed = bcrypt.hashpw(byte_pwd, bcrypt.gensalt())
            modified_users_data[3] = hashed
            users_data[i] = tuple(modified_users_data)

        sql_insert_query_in_users = """ INSERT INTO users (user_email, user_first_name, user_last_name,
                                                    user_password, user_role_id) VALUES (%s,%s,%s,%s,%s) """

        # executemany() to insert multiple rows
        self.postgres.cursor.executemany(sql_insert_query_in_users, users_data)
        self.postgres.connection.commit()
        print("User data inserted successfully into users table")

    # def get_user_by_id(self, user_ID):
    #     sql_select_query_from_user = """SELECT * FROM users WHERE user_id = %s"""
    #     self.postgres.cursor.execute(sql_select_query_from_user, (user_ID))
    #     #self.connection.commit()
    #     record = self.postgres.cursor.fetchone()
    #     print(record)

    def get_user_by_email(self, email):
        sql_select_query_from_user = """SELECT * FROM users WHERE user_email = %s"""
        self.postgres.cursor.execute(sql_select_query_from_user, (email))
        # self.connection.commit()
        record = self.postgres.cursor.fetchone()
        return record

    def delete_user(self, user_ID):
        # Delete user from users table
        sql_delete_query_from_users = """DELETE FROM users WHERE user_id = %s"""
        self.postgres.cursor.execute(sql_delete_query_from_users, (user_ID))
        self.postgres.connection.commit()
        print(f"The user with ID {user_ID} deleted successfully")

    def update_user(self, data_tobe_changed):
        # Update user from users table
        sql_update_query_from_users = """UPDATE users SET user_email=%s, user_first_name=%s, user_last_name=%s, 
                                                        user_password=%s, user_role_id=%s WHERE user_email = %s """

        self.postgres.cursor.executemany(sql_update_query_from_users, data_tobe_changed)
        self.postgres.connection.commit()
        print("User updated!")

    def count_rows(self):
        """
        This function will be user in endpoints.py for checking if users table exists. If its return will be False,
        it means the table users need to be created together with user_roles table.
        """
        self.postgres.cursor.execute("select * from information_schema.tables where table_name=%s", ('users',))
        return bool(self.postgres.cursor.rowcount)


# test = user()
# test.get_user([(1)])
# test.update_user([('antonio@yahoo.com', 'TeoGabriela', 'Popescu', 'teoteoteo', 2, 'antonio@yahoo.com')])
# test.delete_user([(5)])
# test.create_user([('teo@gmail', 'Teo', 'Popescu', 'teoteoteo', 1)])

# test.postgres.close_postgres_connection()
