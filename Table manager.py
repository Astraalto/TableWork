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

def get_tables(cursor):
    cursor.execute("""
        SELECT  name FROM sqlite_master
        WHERE   type = 'table
        AND     name NOT LIKE 'sqlite_%'
        ORDER BY name
                   """)
    return [row[0] for row in cursor.fetchall()]

def get_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info('{table}')")
    return cursor.fetchall()

def validate_date(value):
    parts = value.split("-")
    if len(parts) != 3:
        return False
    y, m, d = parts
    return len(y) == 4 and len(m) == 2 and len(d) == 2 and all(p.isdigit() for p in parts)

def prompt_value(col_name, col_type, nullable=True):
    hint = {
        "TEXT":     "text",
        "INTEGER":  "whole number",
        "REAL":     "decimal number",
        "DATE":     "YYYY-MM-DD",
    }.get(col_type, "value")

    label = f" {col_name} ({hint})"
    if nullable:
        label += " [Enter to leave empty] "
    label += ": "

    while True:
        raw = input(label).strip()

        if raw == "":
            if nullable:
                return None
            else:
                print(f" '{col_name}' cannot be empty")
                continue
        
        if col_type == "INTEGER":
            try:
                return int(raw)
            except ValueError:
                print("Please eneter whole number")

        if col_type == "REAL":
            try:
                return float(raw)
            except ValueError:
                print("Please enter decimal number")

        elif col_type == "DATE":
            if validate_date(raw):
                return raw
            print("Please use YYYY-MM-DD format (e.g. 2024-06-27)")

        else:
            return raw
        
def create_table():
    conn = get_conn()
    cursor = conn.cursor()

    print("\n -- Create new table --\n")
    name = input(" Table name (letters and underscores only): ").strip()
    if not name.replace("_", "").isalpha():
        print("Invalid name")
        conn.close()
        pause()
        return
    
    print(f"\n Define columns for '{name}'.")
    print(" (And 'id' will be added automatically.)\n")

    columns = []
    while True:
        col_name = input (" Column name (or Enter to finish): ").strip()
        if not col_name:
            if not columns:
                print(" Add at least one column")
                continue
            break
        if not col_name.replace("-", "").isalpha():
            print(" Column name: letters and underscores only. ")
            continue
        if col_name.lower() == "id":
            print(" 'id' is reserved for the automatic primary key. ")
            continue