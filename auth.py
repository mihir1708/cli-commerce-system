import sqlite3
from datetime import datetime
from getpass import getpass
import hashlib


def generate_new_uid(conn):
    cur = conn.cursor()
    # Generate a new unique numeric user id 
    cur.execute("SELECT MAX(uid) FROM users")
    row = cur.fetchone()
    
    if row and row[0] is not None:
        new_uid = row[0] + 1
    else:
        new_uid = 10001
    
    return new_uid


def login(conn):
    print("\n Login : Please provide your user ID or email address")
    
    user_input = input("User ID or email address: ").strip()
    pwd = getpass("Enter your password: ")
    cur = conn.cursor()

    # Try login by numeric uid first
    uid_row = None
    try:
        uid_val = int(user_input)
        cur.execute("SELECT uid, role, pwd FROM users WHERE uid = ?", (uid_val,))
        uid_row = cur.fetchone()
    except ValueError:
        uid_row = None

    if uid_row is not None:
        stored_pwd = uid_row[2]
        pwd_bytes = pwd.encode("utf-8")
        pwd_hash = hashlib.sha256(pwd_bytes)
        pwd_hex = pwd_hash.hexdigest()
        if pwd_hex == stored_pwd:
            uid = uid_row[0]
            role = uid_row[1]
            return uid, role

    # Try logging in with email instead
    cur.execute(
        """
        SELECT u.uid, u.role, u.pwd
        FROM users u 
        JOIN customers c ON u.uid = c.cid
        WHERE lower(c.email) = lower(?)
        """,
        (user_input,),
    )
    email_row = cur.fetchone()
    if email_row is not None:
        pwd_bytes = pwd.encode("utf-8")
        pwd_hash = hashlib.sha256(pwd_bytes)
        pwd_hex = pwd_hash.hexdigest()
        if pwd_hex == email_row[2]:
            uid = email_row[0]
            role = email_row[1]
            return uid, role

    # Login failed 
    print("Invalid login credentials. Please try again.")
    return None, None


def signup(conn):
    print("\nSign up: Please provide the following information")
    name = input("Name: ").strip()
    
    # keep asking for email until we get a valid one
    while True:
        email = input("Email address: ").strip()
        
        # Check if email contains @ and .
        if '@' not in email or '.' not in email:
            print("Invalid email format. Please enter a valid email address.")
            continue
        
        # Check if email is not empty
        if not email:
            print("Email address is required.")
            continue
            
        break
    
    pwd = getpass("Password: ")
    cur = conn.cursor()
    # Ensure the provided email is not already in use 
    email_param = (email,)
    cur.execute("SELECT 1 FROM customers WHERE email = ?", email_param)
    existing_email = cur.fetchone()
    
    if existing_email is not None:
        print("Already exisiting email address")
        return None
    # Generate a unique user ID 
    uid = generate_new_uid(conn)
    try:
        # Insert into users first with role automatically set to 'customer'
        # then insert into customers with the same id 
        pwd_bytes = pwd.encode("utf-8")
        pwd_hash = hashlib.sha256(pwd_bytes)
        hashed_pwd = pwd_hash.hexdigest()
        user_insert_params = (uid, hashed_pwd, "customer")
        cur.execute("INSERT INTO users(uid, pwd, role) VALUES(?,?,?)", user_insert_params)
        customer_insert_params = (uid, name, email)
        cur.execute("INSERT INTO customers(cid, name, email) VALUES(?,?,?)", customer_insert_params)
        conn.commit()
        print(f"Registered. Your User ID is {uid}.")
        return uid
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print("Registration failed:", e)
        return None