import psycopg2

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

InsertUser([('toni@yahoo.com', 'Toni', 'Paraschiv', 'tonibogdan21', 1)])
