import bcrypt
import re

from DB_PostgreSQL import Postgres


def create_user_prerequisites(request_data):
    user_update = request_data.get('update', None)  # returns json value if exists, else returns None

    if type(user_update) is not bool:
        return None

    new_user = {
        'user_email': request_data.get('user_email', None),
        'first_name': request_data.get('first_name', None),
        'last_name': request_data.get('last_name', None),
        'user_password': request_data.get('user_password', None),
        'user_role_id': request_data.get('user_role_id', None)
    }
    # check if client did not provide a required row. If a key has a None value return request for required row
    for name, val in new_user.items():
        if val is None:
            return False, name
    return True, new_user


def check_regex(data):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, data)


def hash_password(users_data):
    modified_users_data = list(users_data[0])
    byte_pwd = modified_users_data[3].encode('utf-8')
    hashed = bcrypt.hashpw(byte_pwd, bcrypt.gensalt())
    modified_users_data[3] = hashed.decode('utf-8')
    return tuple(modified_users_data)


class User:

    def __init__(self):
        self.postgres = Postgres()

    def create_user(self, users_data):

        users_data[0] = hash_password(users_data)

        sql_insert_query_in_users = """INSERT INTO users (user_email, user_first_name, user_last_name, user_password, 
        user_role_id) VALUES (%s,%s,%s,%s,%s) returning user_email """

        self.postgres.cursor.executemany(sql_insert_query_in_users, users_data)
        row_modified = self.postgres.cursor.rowcount  # returns 1 if table affected
        self.postgres.connection.commit()
        if row_modified == 1:
            print("User data inserted successfully into users table")
            return True
        return False

    def add_user(self, new_user):

        if not self.count_rows('users') and not self.count_rows('user_roles'):  # if both tables do not exist
            if self.postgres.check_user_roles() and self.postgres.check_users():  # if both tables could be created
                if self.postgres.create_user_roles():  # if admin and viewer could be added
                    print("user_roles table up and running - admin and viewer columns inserted successfully into table")
                    print("users table up and running!")
                else:
                    return "userRolesTableAddFailed"
            elif not self.postgres.check_user_roles():
                return "userRolesCreationFailed"
            elif not self.postgres.check_users():
                return "usersCreationFailed"
            else:
                return "bothTablesFailed"
        elif self.count_rows('user_roles') and not self.count_rows('users'):  # if user_roles exists but users does not
            if not self.postgres.check_users():  # if users could not be created
                return "usersCreationFailed"
            else:
                print("users table up and running.")
        elif self.count_rows('user_roles') and self.count_rows('users'):  # if both table exists check if admin and viewer exist
            if self.postgres.create_user_roles():  # if admin and viewer could be added or already existed
                print("admin and viewer columns exist in user_roles table")
            else:
                return "userRolesExistsButFailed"
        # no need to test the case when users table exists and user_roles does not because it can't be possible
        # because of the foreign key constraint
        else:  # just for testing
            print("Both table existed and all went good")

        new_user_data_to_tuple = [tuple(new_user.values())]
        if self.create_user(new_user_data_to_tuple):  # if user successfully created return user
            return new_user
        else:
            return "generalFail"

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

    def update_user(self, data_tobe_changed=None, old_email=None):
        # Update user from users table
        data_tobe_changed = hash_password([tuple(data_tobe_changed)])  # return same data but with hashed password

        new_user_data_to_tuple = [tuple(data_tobe_changed)]
        add_email_at_end = list(new_user_data_to_tuple[0])
        if old_email is None:
            add_email_at_end.append(new_user_data_to_tuple[0][0])
        else:
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

    def postman_update_user_by_email(self, new_user, user_old_email):
        if user_old_email is None:
            return None
        elif user_old_email:
            if not check_regex(user_old_email):
                return "invalidEmail"
            print("Also change the email to a new email.")
            if self.update_user(new_user.values(), old_email=user_old_email):
                new_user['user_new_email'] = new_user.pop('user_email')
                return new_user
            else:
                return "userUpdateFail"
        elif not user_old_email:
            print("No require to change the email to a new email.")
            if self.update_user(new_user.values()):  # if user successfully updated return user
                return new_user
            else:
                return "userUpdateFail"
        else:  # pe asta il las asa just in case, desi cred ca am acoperit toate variantele prin cele 3 conditii
            return "generalFail"

    def count_rows(self, table):
        # This function will be used in endpoints.py for checking if table exists
        self.postgres.cursor.execute("select * from information_schema.tables where table_name=%s", (table,))
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
