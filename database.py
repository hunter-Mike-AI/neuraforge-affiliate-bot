import os
import psycopg2 # Necesitas añadirlo a requirements.txt

# Si Railway te da DATABASE_URL, úsala; si no, usa sqlite (solo para pruebas)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    # Backup local si no hay nube
    import sqlite3
    return sqlite3.connect("data.db", check_same_thread=False)

