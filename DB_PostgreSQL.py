import psycopg2

def CreateDB():
    global connection, cursor
    try:
        # open database connection
        connection = psycopg2.connect(
            host = "localhost",
            database = "projectuser",
            user = "postgres",
            password = "tonibogdan21"
        )

        cursor = connection.cursor()

        # Verify if the user_roles table exists - if not then create table, also check if the 2 roles exist - if not create the 2 roles
        def VerifyUserRoles():
            # check if the table exists
            sql_create_table_user_roles = """CREATE TABLE IF NOT EXISTS user_roles (
                        role_id INT,
	                    role_description VARCHAR(50) NOT NULL, 
                    	PRIMARY KEY (role_id)
                )
                """
            cursor.execute(sql_create_table_user_roles)
            connection.commit()

            # add the 2 roles if they not exist
            sql_number_roles = """SELECT COUNT(1) FROM user_roles"""
            cursor.execute(sql_number_roles)
            result = cursor.fetchone()
            if result[0] == 0:
                roles = [(1, 'admin'), (2, 'viewer')]
                sql_insert_two_roles = """ INSERT INTO user_roles (role_id, role_description)
                                             VALUES (%s,%s) """
                cursor.executemany(sql_insert_two_roles, roles)
                connection.commit()
                print("User roles - admin and viewer - inserted successfully into user_roles table")
            print("user_roles table up and running!")

        VerifyUserRoles()

        # Verify if the users table exists, if not then create table
        def VerifyUsers():
            sql_create_table_users = """CREATE TABLE IF NOT EXISTS users (
                        user_id INT GENERATED ALWAYS AS IDENTITY,
	                    user_email VARCHAR(50), 
	                    user_first_name VARCHAR(30) NOT NULL,
                    	user_last_name VARCHAR(30) NOT NULL,
                    	user_password TEXT NOT NULL,
                    	user_role_id INT REFERENCES user_roles(role_id) ON DELETE SET NULL,
                    	PRIMARY KEY (user_id, user_email)
                )
                """
            cursor.execute(sql_create_table_users)
            connection.commit()
            print("users table up and running!")

        VerifyUsers()

    except (Exception, psycopg2.Error) as error:
        print("Error - operation failed: {}".format(error))

    finally:
        # closing database connection
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

CreateDB()
