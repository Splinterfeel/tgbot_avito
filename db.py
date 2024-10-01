import sqlite3
import os
from pathlib import Path

DB_PATH = Path(os.getcwd(), 'main.db')

def init() -> None:
    if not os.path.isfile(DB_PATH):
        create_new_db()


def create_new_db():
    print('init new db')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE users
                   (
                    username VARCHAR(400) NOT NULL,
                    client_id VARCHAR(400) NOT NULL,
                    client_secret VARCHAR(400) NOT NULL,
                    UNIQUE(username, client_id, client_secret)
                   )''')
    conn.commit()
    conn.close()


def add_client_info(username, client_id, client_secret):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (username, client_id, client_secret)
                   VALUES (?, ?, ?)''',
                   [username, str(client_id), str(client_secret)])
    conn.commit()
    conn.close()


def get_client_info(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', [username])
    columns = [x[0] for x in cursor.description]
    result = cursor.fetchall()
    result = [dict(zip(columns, x)) for x in result]
    conn.close()
    if result:
        return result[0]
    return None
