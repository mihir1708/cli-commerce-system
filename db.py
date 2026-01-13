import os
import sqlite3
import hashlib


DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")


def connect_db(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # Enforce foreign key constraints declared in schema
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    cur = conn.cursor()
    # Drop existing tables to reset schema
    cur.execute("drop table if exists orderlines")
    cur.execute("drop table if exists orders")
    cur.execute("drop table if exists cart")
    cur.execute("drop table if exists search")
    cur.execute("drop table if exists viewedProduct")
    cur.execute("drop table if exists sessions")
    cur.execute("drop table if exists products")
    cur.execute("drop table if exists customers")
    cur.execute("drop table if exists users")
    # good
    cur.execute(
        """
        create table users (
            uid		int,
            pwd		text,
            role		text,
            primary key (uid)
        )
        """
    )
    # good
    cur.execute(
        """
        create table customers (
            cid		int,
            name		text, 
            email		text,
            primary key (cid),
            foreign key (cid) references users
        )
        """
    )
    # good
    cur.execute(
        """
        create table products (
            pid		int, 
            name		text, 
            category	text, 
            price		float, 
            stock_count	int, 
            descr		text,
            primary key (pid)
        )
        """
    )
    # probably shud have ono and cid and sessionNo as primary key
    # and have a foreign key constraint to the orders table
    # Create sessions before orders to satisfy FKs
    cur.execute(
        """
        create table sessions (
            cid		int,
            sessionNo	int, 
            start_time	datetime, 
            end_time	datetime,
            primary key (cid, sessionNo),
            foreign key (cid) references customers on delete cascade
        )
        """
    )
    cur.execute(
        """
        create table viewedProduct (
            cid		int, 
            sessionNo	int, 
            ts		timestamp, 
            pid		int,
            primary key (cid, sessionNo, ts),
            foreign key (cid, sessionNo) references sessions,
            foreign key (pid) references products
        )
        """
    )
    cur.execute(
        """
        create table search (
            cid		int, 
            sessionNo	int, 
            ts		timestamp, 
            query		text,
            primary key (cid, sessionNo, ts),
            foreign key (cid, sessionNo) references sessions
        )
        """
    )
    cur.execute(
        """
        create table cart (
            cid		int, 
            sessionNo	int, 
            pid		int,
            qty		int,
            primary key (cid, sessionNo, pid),
            foreign key (cid, sessionNo) references sessions,
            foreign key (pid) references products
        )
        """
    )
    cur.execute(
        """
        create table orders (
            ono		int, 
            cid		int,
            sessionNo	int,
            odate		date, 
            shipping_address text,
            primary key (ono),
            foreign key (cid, sessionNo) references sessions
        )
        """
    )
    cur.execute(
        """
        create table orderlines (
            ono		int, 
            lineNo	int, 
            pid		int, 
            qty		int, 
            uprice	float, 
            primary key (ono, lineNo),
            foreign key (ono) references orders on delete cascade
        )
        """
    )
    
    
    

    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users(uid, pwd, role) VALUES(?,?,?)",
            (1, hashlib.sha256("sales".encode("utf-8")).hexdigest(), "sales"),
        )

    cur.execute("SELECT COUNT(*) AS c FROM products")
    if cur.fetchone()[0] == 0:
        products = [
            (1, "Widget A", "gadgets", 9.99, 50, "Basic widget A"),
            (2, "Widget B", "gadgets", 14.99, 30, "Improved widget B"),
            (3, "Gizmo C", "tools", 24.50, 20, "Handy gizmo C"),
            (4, "Gizmo D", "tools", 49.00, 10, "Heavy-duty gizmo D"),
            (5, "Thing E", "misc", 5.00, 100, "Small thing E"),
            (6, "Thing F", "misc", 6.50, 80, "Small thing F"),
        ]
        cur.executemany(
            "INSERT INTO products(pid, name, category, price, stock_count, descr) VALUES(?,?,?,?,?,?)",
            products,
        )

    conn.commit()


