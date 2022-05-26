1. Install Postgres (pgAdmin 4)
- connect to postgres -> psql -U postgres
- create DB - CREATE DATABASE nameForDatabaseAsYouWish
- check the DB you created by going to PgAdmin 4 UI, Servers -> PostgreSQL 14 -> Databases -> choose the DB name you provided earlier ->
Schemas -> Tables (you will not have any table there until you first insert a user with Postman)

2. After having Postgres DB working, and also you cloned the code from GitHub to your IDE (PyCharm for example):
- run endpoints.py by going to Pycharm terminal and type: python .\endpoints.py
- after running it, if you get a web domain in terminal similar to http://127.0.0.1:5000/ it means the app is working
- leave it open as time as you do Postman requests. After you finish you can press Ctrl + C and stop the Flask connection

3. Open Postman and try one of the provided requests
(to see the results of the request you did in Postman, go to pgAdmin 4, right click and press Refresh on 'Tables'. After
the first user inserted you should see 2 tables added (users and user_roles) after refreshing.
To see the table data look above the "Server" where you will see Browser, and
on the right of Browser you will have the first icon 'Query Tool'. Click on it and you will be able to write SQL. For example
you can see the tables data by writing "select * from users/user_roles" and press F5)

- to insert a user:   -> choose 'Body', then 'raw' and type:
{
    "update":false,
    "user_old_email":"",
    "user_email":"tonibogdan21@yahoo.com",
    "first_name":"Antonio",
    "last_name":"Bogdan",
    "user_password":"toni2121",
    "user_role_id":1
}
- to update a user without updating the user email (which is the primary key in DB):   -> choose 'Body', then 'raw' and type:
{
    "update":true,
    "user_old_email":"",
    "user_email":"tonibogdan21@yahoo.com",
    "first_name":"changeDataHere",
    "last_name":"orHere",
    "user_password":"orHere",
    "user_role_id":alsoHereIfUWant
}
- to update a user and also update the user email to a new one:   -> choose 'Body', then 'raw' and type:
{
    "update":true,
    "user_old_email":"theNewEmailHere",
    "user_email":"tonibogdan21@yahoo.com(which is the old email you want to change)",
    "first_name":"changeDataHere",
    "last_name":"orHere",
    "user_password":"orHere",
    "user_role_id":alsoHereIfUWant
}
- to get a user by user email:
http://127.0.0.1:5000/users/tonibogdan@yahoo.com(or any other email you want to get user informations from)
- to delete a user:
http://127.0.0.1:5000/users/tonibogdan@yahoo.com(or any other user email you want to delete from DB)
- to login   -> choose 'Body', then 'raw' and type:
{
    "user_email":"tonibogdan21@yahoo.com(or any other email you want to login to)",
    "user_password":"toni2121(or the password you know you chose for your account)"
}


