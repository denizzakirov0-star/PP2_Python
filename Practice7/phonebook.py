import csv
import psycopg2
from config import load_config


def insert_rows(contacts):
    sql = """INSERT INTO phonebook (name, phone) VALUES (%s, %s)"""
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, contacts)
                conn.commit()
    except Exception as error:
        print(error)


def csv_reader():
    path = input("Type the path of csv file: ")
    data = []
    with open(path, "r") as contacts:
        reader = csv.reader(contacts)
        for row in reader:
            data.append((row[0], row[1]))
    insert_rows(data)
    print("Contact(s) added")

def console_reader():
    row = input().split(",")
    insert_rows([(row[0],row[1])])


def update_contact():
    choice = input("What do you want to update (name/phone): ")
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if choice == "name":
                    old_phone = input("Enter contact phone: ")
                    cur.execute(
                        "SELECT id FROM phonebook WHERE phone = %s",
                        (old_phone,)
                    )
                    if cur.fetchone() is None:
                        print("Contact not found")
                        return
                    new_name = input("Enter new name: ")
                    cur.execute(
                        "UPDATE phonebook SET name = %s WHERE phone = %s",
                        (new_name, old_phone)
                    )
                    conn.commit()
                    print("Name updated")
                elif choice == "phone":
                    old_phone = input("Enter old phone: ")
                    cur.execute(
                        "SELECT id FROM phonebook WHERE phone = %s",
                        (old_phone,)
                    )
                    if cur.fetchone() is None:
                        print("Contact not found")
                        return
                    new_phone = input("Enter new phone: ")
                    cur.execute(
                        "UPDATE phonebook SET phone = %s WHERE phone = %s",
                        (new_phone, old_phone)
                    )
                    conn.commit()
                    print("Phone updated")
                else:
                    print("Invalid choice")
    except Exception as error:
        print(error)


def search_contact():
    choice = input("Search by name or phone prefix? (name/phone): ")
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if choice == "name":
                    name = input("Enter name: ")
                    cur.execute(
                        "SELECT id, name, phone FROM phonebook WHERE name ILIKE %s",
                        (f"%{name}%",)
                    )
                    rows = cur.fetchall()
                    if not rows:
                        print("No contacts found")
                        return
                    for id, name, phone in rows:
                        print(id, name.strip(), phone)
                elif choice == "phone":
                    prefix = input("Enter phone prefix (e.g. +7, +1): ")
                    cur.execute(
                        "SELECT id, name, phone FROM phonebook WHERE phone LIKE %s",
                        (f"{prefix}%",)
                    )
                    rows = cur.fetchall()
                    if not rows:
                        print("No contacts found")
                        return
                    for id, name, phone in rows:
                        print(id, name.strip(), phone)
                else:
                    print("Invalid choice")

    except Exception as error:
        print(error)

def delete_contact():
    choice = input("Delete by name or phone? (name/phone): ")
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if choice == "name":
                    name = input("Enter name: ")
                    cur.execute(
                        "SELECT id FROM phonebook WHERE name = %s",
                        (name,)
                    )
                    if cur.fetchone() is None:
                        print("Contact not found")
                        return
                    cur.execute(
                        "DELETE FROM phonebook WHERE name = %s",
                        (name,)
                    )
                    conn.commit()
                    print("Contact(s) deleted")
                elif choice == "phone":
                    phone = input("Enter phone: ")
                    cur.execute(
                        "SELECT id FROM phonebook WHERE phone = %s",
                        (phone,)
                    )
                    if cur.fetchone() is None:
                        print("Contact not found")
                        return
                    cur.execute(
                        "DELETE FROM phonebook WHERE phone = %s",
                        (phone,)
                    )
                    conn.commit()
                    print("Contact(s) deleted")
                else:
                    print("Invalid choice")
    except Exception as error:
        print(error)

# update_contact()

# csv_reader()

# console_reader()

# search_contact()

# delete_contact()