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

        print(f" Column type for '{col_name}':")
        for i, t in enumerate(COLUMN_TYPES, 1):
            print(f"   {i},  {t}")
            while True:
                t_choice = input(" Pick type: ").strip()
                if t_choice.isdigit() and 1 <= int(t_choice) <= len(COLUMN_TYPES):
                    col_type = COLUMN_TYPES[int(t_choice) -1]
                    break
                print(" Invalid choice.")

            nullable = input(f" Is '{col_name}' required ? (Y/N): ").strip().lower() == "y"
            not_null = "NOT NULL" if nullable else ""

            columns.append((col_name, col_type, not_null))
            print(f"  Column added: {col_name}  ({col_type}{ 'NOT NULL' if not_null else ''})\n")


    col_defs = ",\n           ".join(
        f"{col_name} {col_type} {not_null}".strip()
        for col_name, col_type, not_null in columns
        )
    sql = f"""CREATE TABLE {name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                {col_defs}
        )"""
    print(f"\n  SQL preview:\n{sql}")
    confirm = input("  Create this table (Y/N): ").strip().lower()
    if confirm == "y":
            cursor.execute(sql)
            conn.commit()
            print(f"\n Table '{name}' created.")
    else:
            print("  Concelled.")

    conn.close()
    pause()


def edit_row():
    conn = get_conn()
    cursor = conn.cursor()
    table = pick_table(cursor)
    if not table:
        conn.close()
        return
    
    cols = get_columns(cursor, table)
    col_names = [c[1] for c in cols]

    cursor.execute(f"SELECT * FROM '{table}'")
    rows = cursor.fetchall()

    if not rows:
        print(f"\n  '{table}' is empty.")
        conn.close()
        pause()
        return
    
    print(f"\n Rows in '{table}' :\n")
    for row in rows:
        summary = "  |  ".join(f"{col_names[i]}: {v}" for i, v in enumerate(row))
        print(f"   {summary}")

    row_id = input("\n Enter the ID of the row to edit (or 0 to cancel): ").strip()
    if row_id == "0" or not row_id.isdigit():
        conn.close()
        return
    
    cursor.execute(f"SELECT * FROM '{table}' WHERE id = ?")
    row = cursor.fetchone()
    if not row:
        print(f"   No row with ID {row_id}.")
        conn.close()
        pause()
        return
    
    print(f"\n Editing row ID {row_id}. Press Enter to keep current value.\n")

    data_cols = [c for c in cols if c[1] != "id"]
    current = {c[1]: row[i + 1] for i, c in enumerate(data_cols)}
    updates = {}

    for col in data_cols:
        col_name = col[1]
        col_type = col[2]
        current_val = current[col_name]
        print(f" Current{col_name}: {current_val}")
        new_val = prompt_value(col_name, col_type, nullable=True)
        updates[col_name] = new_val if new_val is not None else current_val

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    cursor.execute(
        f"UPDATE  '{table}' SET {set_clause} WHERE id = ?",
        list(updates.values()) + [int(row_id)]
    )
    conn.commit()
    print(f"\n  Row ID  {row_id} updated.")
    conn.close()
    pause()
        

def drop_table():
    conn = get_conn()
    cursor = conn.cursor()

    print("\n  -- Create a new table --\n")
    name = input("  Tbale name (lettter and underscores only): ").strip()
    if not name.replace("_", "").isalpha():
        print("  Invalid name. use only letters and underscores.")
        conn.close()
        pause()
        return
    
    if name in get_tables(cursor):
        print("  Table '{name}' already exists.")
        conn.close()
        pause()
        return
    
    print(f"\n Define columns for '{name}.")
    print("   (An 'id' primary key column will be added automatically.)\n")