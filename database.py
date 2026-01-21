# database.py
import sqlite3
import os

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliates (
            user_id INTEGER PRIMARY KEY,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('data.db')
