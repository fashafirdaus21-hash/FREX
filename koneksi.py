import mysql.connector

def buat_koneksi():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_perpustakaan"
    )
    return conn