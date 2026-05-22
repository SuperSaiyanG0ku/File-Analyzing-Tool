import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="proxies.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            ip TEXT,
            port TEXT,
            username TEXT,
            password TEXT,
            proxy_type TEXT
        );
        """
        with self.get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def add_proxy(self, country, ip, port, proxy_type, username="", password=""):
        query = "INSERT INTO proxies (country, ip, port, proxy_type, username, password) VALUES (?, ?, ?, ?, ?, ?)"
        with self.get_connection() as conn:
            conn.execute(query, (country, ip, port, proxy_type, username, password))
            conn.commit()

    def get_all_proxies(self):
        query = "SELECT * FROM proxies"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def delete_proxy(self, proxy_id):
        query = "DELETE FROM proxies WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(query, (proxy_id,))
            conn.commit()

    def search_proxies(self, search_term):
        query = "SELECT * FROM proxies WHERE country LIKE ? OR ip LIKE ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
            return cursor.fetchall()
