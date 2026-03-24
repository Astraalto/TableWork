import sqlite3
import os

DB_FILE = "table.db"
COLUMN_TYPES = ["TEXT", "INTEGER", "REAL", "DATE"] 

def get_conn():
    return sqlite3.connect(DB_FILE)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\n Press Enter to continue...")

def get_table(cursor):
    cursor.execute("""
        SELECT  name FROM sqlite_master
        WHERE   type = 'table
        AND     name NOT LIKE 'sqlite_%'
        ORDER BY name
                   """)
    return [row[0] for row in cursor.fetchall()]