import sqlite3
import os


def setup_database():
    """
    Create the `user_string` table in the database
    on server startup
    """
    DB_STRING = os.getenv("DBNAME")
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE providers (email, verified)")


def cleanup_database():
    """
    Destroy the `user_string` table from the database
    on server shutdown.
    """
    DB_STRING = os.getenv("DBNAME")
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE providers")

