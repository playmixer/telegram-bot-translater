import sqlite3


def connect():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()
    return cursor


class DBConnect(object):
    record = None

    def __init__(self):
        self.conn = sqlite3.connect('sqlite.db')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()

    def __enter__(self):
        self.conn = sqlite3.connect('sqlite.db')
        self.cursor = self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

    def select(self, query: str):
        self.cursor.execute(query)
        self.record = self.cursor

        return self

    def all(self):
        return self.record.fetchall()
