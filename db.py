import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",   # 👉 apna MySQL password yahan likh
        database="attendance_db"
    )
