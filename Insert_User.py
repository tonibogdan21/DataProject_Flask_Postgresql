import psycopg2
import bcrypt

def InsertUser(users_data):
    global cursor, connection
    try:
        # open database connection
        connection = psycopg2.connect(
            host="localhost",
            database="projectuser",
            user="postgres",
            password="tonibogdan21"
        )

        cursor = connection.cursor()

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
        cursor.executemany(sql_insert_query_in_users, users_data)
        connection.commit()
        print("User data inserted successfully into users table")

    except (Exception, psycopg2.Error) as error:
        print("Failed inserting user data into users table: {}".format(error))

    finally:
        # closing database connection
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

InsertUser([('bogdan@yahoo.com', 'Toni', 'Paraschiv', 'tonibogdan21', 1), ('bogdan21@yahoo.com', 'Toni', 'Paraschiv', 'tonibogdan212121', 1)])
