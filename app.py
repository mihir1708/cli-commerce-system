import sys
from db import connect_db, init_db
from auth import login, signup
from sessions import start_customer_session, end_customer_session
from customer import customer_menu as _customer_menu
from sales import sales_menu


def main_menu():
    print("\n=== Welcome to the Store CLI ===")
    print("1) Login")
    print("2) Sign up")
    print("0) Exit")
    choice = input("Choose: ").strip()
    return choice


def customer_menu(conn, cid):
    session_no = start_customer_session(conn, cid)
    try:
        _customer_menu(conn, cid, session_no)
    finally:
        end_customer_session(conn, cid, session_no)

def run():
    if len(sys.argv) > 1:
        db_path = sys.argv[1] 
    else:
        db_path = None
    conn = connect_db(db_path)
    # Only initialize schema when no DB path is provided.
    if db_path is None:
        init_db(conn)
    while True:
        choice = main_menu()
        if choice == "1":
            uid, role = login(conn)
            if role == "customer":
                customer_menu(conn, uid)  # uid == cid by design
            elif role == "sales":
                sales_menu(conn)
        elif choice == "2":
            uid = signup(conn)
            if uid:
                customer_menu(conn, uid)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")
    conn.close()

if __name__ == "__main__":
    run()