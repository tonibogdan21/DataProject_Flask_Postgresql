import bcrypt
import re

from DB_PostgreSQL import Postgres


class user:

    def __init__(self):
        self.postgres = Postgres()

    def create_user(self, users_data):

        users_data[0] = self.hash_password(users_data)

        sql_insert_query_in_users = """INSERT INTO users (user_email, user_first_name, user_last_name, user_password, 
        user_role_id) VALUES (%s,%s,%s,%s,%s) returning user_email """

        # executemany() to insert multiple rows
        self.postgres.cursor.executemany(sql_insert_query_in_users, users_data)
        row_modified = self.postgres.cursor.rowcount  # returns 1 if table affected
        self.postgres.connection.commit()
        if row_modified == 1:
            print("User data inserted successfully into users table")
            return True
        return False

    def hash_password(self, users_data):
        modified_users_data = list(users_data[0])
        byte_pwd = modified_users_data[3].encode('utf-8')
        hashed = bcrypt.hashpw(byte_pwd, bcrypt.gensalt())
        modified_users_data[3] = hashed.decode('utf-8')
        return tuple(modified_users_data)

    def get_user_data_by_email(self, email):
        sql_select_query_from_user = """SELECT * FROM users WHERE user_email = %s"""
        self.postgres.cursor.execute(sql_select_query_from_user, email)
        record = self.postgres.cursor.fetchone()
        if record:
            existing_user = {
                'user_email': record[1],
                'first_name': record[2],
                'last_name': record[3],
                'user_role_id': record[5]
            }
            return existing_user
        else:
            return None

    def delete_user(self, email):
        # Delete user from users table
        sql_delete_query_from_users = """DELETE FROM users WHERE user_email = %s"""
        self.postgres.cursor.execute(sql_delete_query_from_users, email)
        row_deleted = self.postgres.cursor.rowcount  # returns 1 if table affected
        self.postgres.connection.commit()
        if row_deleted == 1:
            return True
        return False

    def update_user(self, data_tobe_changed, old_email=None):
        # Update user from users table
        data_tobe_changed = self.hash_password([tuple(data_tobe_changed)])  # return same data but with hashed password
        if old_email is None:
            new_user_data_to_tuple = [tuple(data_tobe_changed)]
            add_email_at_end = list(new_user_data_to_tuple[0])
            add_email_at_end.append(new_user_data_to_tuple[0][0])
            new_user_data_to_tuple = [tuple(add_email_at_end)]
        else:
            new_user_data_to_tuple = [tuple(data_tobe_changed)]
            add_email_at_end = list(new_user_data_to_tuple[0])
            add_email_at_end.append(old_email)
            new_user_data_to_tuple = [tuple(add_email_at_end)]

        sql_update_query_from_users = """UPDATE users SET user_email=%s, user_first_name=%s, user_last_name=%s, 
                                                        user_password=%s, user_role_id=%s WHERE user_email = %s """

        self.postgres.cursor.executemany(sql_update_query_from_users, new_user_data_to_tuple)
        row_modified = self.postgres.cursor.rowcount  # returns 1 if table affected
        self.postgres.connection.commit()
        if row_modified == 1:
            print("User updated!")
            return True
        return False

    def count_rows(self):
        """
        This function will be user in endpoints.py for checking if users table exists. If its return will be False,
        it means the table users need to be created together with user_roles table.
        """
        self.postgres.cursor.execute("select * from information_schema.tables where table_name=%s", ('user_roles',))
        return bool(self.postgres.cursor.rowcount)

    def track_exists(self, email):
        self.postgres.cursor.execute("SELECT user_email FROM users WHERE user_email = %s", email)
        return self.postgres.cursor.fetchone() is not None  # returns True if the provided user_email exists in DB

    def check_match(self, email, input_password):
        sql_select_query_from_user = """SELECT user_password FROM users WHERE user_email = %s"""
        self.postgres.cursor.execute(sql_select_query_from_user, email)
        record = self.postgres.cursor.fetchone()
        if record is None:
            return False
        if bcrypt.checkpw(input_password, record[0].encode('utf-8')):
            user_data = self.get_user_data_by_email(email)
            return user_data
        else:
            return None

    def check_regex(self, data):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.search(regex, data)
