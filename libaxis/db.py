import sqlite3


def _init_db():
    conn = sqlite3.connect("axisbot.db")
    return conn


DB = _init_db()
