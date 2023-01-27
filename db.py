import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import errorcode
import requests


class DB_Back():
    def __init__(self, host, port, user, password, db_name):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name

        self.mydb = self.connect()

        self.db_cursor = self.mydb.cursor()
        self.crete_tables()

    def connect(self):

        try:
            mydb = mysql.connector.connect(
                host=self.host, port=self.port, user=self.user, password=self.password, database=self.db_name)
            return mydb
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def crete_tables(self):
        self.db_cursor.execute(
            "CREATE TABLE IF NOT EXISTS user (id int PRIMARY KEY AUTO_INCREMENT, username varchar(255) NOT NULL, password varchar(255) NOT NULL, created_at datetime);")
        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS url (id int PRIMARY KEY AUTO_INCREMENT, address varchar(255) NOT NULL, user_id int NOT NULL, created_at datetime, threshold int NOT NULL, failed_times int DEFAULT 0, FOREIGN KEY (user_id) REFERENCES user(id));")
        self.db_cursor.execute(
            "CREATE TABLE IF NOT EXISTS request (id int PRIMARY KEY AUTO_INCREMENT, url_id int NOT NULL, created_at datetime, result int, FOREIGN KEY (url_id) REFERENCES url(id));")

    def get_tables(self):
        self.db_cursor.execute("Show tables;")
        myresult = self.db_cursor.fetchall()

        tables = []
        for x in myresult:
            tables.append(x[0])

        return tables

    def get_db_url(self):
        return f"mysql+mysqldb://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

    def periodic_request(self):
        try:
            self.db_cursor.execute("SELECT * FROM url")
            myresult = self.db_cursor.fetchall()

            for x in myresult:
                url = x[1]
                req = requests.get(url)
                status_code = req.status_code
                insert = f"INSERT INTO request (url_id, result) VALUES ({x[0]}, {status_code})"
                self.db_cursor.execute(insert)
                self.mydb.commit()
                if status_code < 200 or status_code >= 300:
                    print(status_code)
                    update = f"UPDATE url SET failed_times = failed_times+1 where id={x[0]}"
                    self.db_cursor.execute(update)
                self.mydb.commit()
        except:
            pass
