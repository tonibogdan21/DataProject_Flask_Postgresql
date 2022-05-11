import bcrypt
from DB_PostgreSQL import Postgres

class user(Postgres):

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
        self.cursor.executemany(sql_insert_query_in_users, users_data)
        self.connection.commit()
        print("User data inserted successfully into users table")

    def get_user_by_id(self, user_ID):
        sql_select_query_from_user = """SELECT * FROM users WHERE user_id = %s"""
        self.cursor.execute(sql_select_query_from_user, (user_ID))
        #self.connection.commit()
        record = self.cursor.fetchone()
        print(record)

    def get_user_by_email(self, email):
        sql_select_query_from_user = """SELECT * FROM users WHERE user_email = %s"""
        self.cursor.execute(sql_select_query_from_user, (email))
        #self.connection.commit()
        record = self.cursor.fetchone()
        return record

    def delete_user(self, user_ID):
        # Delete user from users table
        sql_delete_query_from_users = """DELETE FROM users WHERE user_id = %s"""
        self.cursor.execute(sql_delete_query_from_users, (user_ID))
        self.connection.commit()
        print(f"The user with ID {user_ID} deleted successfully")

    def update_user(self, column_name, data_tobe_changed_and_user_ID):
        # Update user from users table
        if column_name == 'email':
            sql_update_query_from_users = """UPDATE users SET user_email = %s WHERE user_id = %s"""
            self.cursor.executemany(sql_update_query_from_users, data_tobe_changed_and_user_ID)
            self.connection.commit()
            print(f"The user with ID {data_tobe_changed_and_user_ID[0][1]} changed his/her user_email to {data_tobe_changed_and_user_ID[0][0]}")
        elif column_name =='first name':
            sql_update_query_from_users = """UPDATE users SET user_first_name = %s WHERE user_id = %s"""
            self.cursor.executemany(sql_update_query_from_users, data_tobe_changed_and_user_ID)
            self.connection.commit()
            print(f"The user with ID {data_tobe_changed_and_user_ID[0][1]} changed his/her user_first_name to {data_tobe_changed_and_user_ID[0][0]}")
        elif column_name =='last name':
            sql_update_query_from_users = """UPDATE users SET user_last_name = %s WHERE user_id = %s"""
            self.cursor.executemany(sql_update_query_from_users, data_tobe_changed_and_user_ID)
            self.connection.commit()
            print(f"The user with ID {data_tobe_changed_and_user_ID[0][1]} changed his/her user_last_name to {data_tobe_changed_and_user_ID[0][0]}")
        elif column_name =='role id':
            sql_update_query_from_users = """UPDATE users SET user_role_id = %s WHERE user_id = %s"""
            self.cursor.executemany(sql_update_query_from_users, data_tobe_changed_and_user_ID)
            self.connection.commit()
            print(f"The user with ID {data_tobe_changed_and_user_ID[0][1]} changed his/her user_role_id to {data_tobe_changed_and_user_ID[0][0]}")
        else:
            print('Please provide a valid column_name: email, first name, last name or role id.')

#test = user()
#test.connect_to_postgres()
#test.get_user([(1)])
#test.update_user('role id', [(2, 1)])
#test.delete_user([(5)])
#test.create_user([('toni21@yahoo.com', 'Bogdan', 'Paraschiv', 'tonibogdan212121', 2)])
#test.close_postgres_connection()
