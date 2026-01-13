# CLI Commerce System

A Python-based command-line e-commerce application featuring user authentication, product search, cart management, order processing, and sales analytics using SQLite.

---

## 📌 Overview

This project is a terminal-based e-commerce system built with Python and SQLite.
It supports customer and salesperson roles, secure login, product browsing, shopping cart operations, order checkout, and basic sales reporting.

The application focuses on backend logic, database design, and modular Python code, using only the Python standard library.

---

## 🚀 Features

**Customers**

* Signup and login with hashed passwords
* Product search with pagination
* View product details and activity tracking
* Shopping cart management
* Order checkout and order history

**Salesperson**

* Update product price and stock
* Weekly sales summary
* Top products by orders and views

---

## 🗂️ Project Structure

```
app.py        # Entry point
auth.py       # Authentication logic
customer.py   # Customer features
sales.py      # Salesperson features
sessions.py   # Session tracking
db.py         # Database setup and connection
```

---

## ▶️ How to Run

**Requirements:** Python 3

Run with a local database (auto-created if missing):

```bash
python3 app.py
```

Run with an existing database:

```bash
python3 app.py /path/to/database.db
```

---

## 🔑 Default Login (New Database)

* **Salesperson ID:** `1`
* **Password:** `sales`

Customers can register directly from the application.

---

## 🛠️ Tech Stack

* Python 3
* SQLite (`sqlite3`)
* SHA-256 password hashing
* No external dependencies

---

## 📄 Notes

* Uses parameterized SQL queries
* Enforces relational integrity with foreign keys
* Designed for educational and backend practice
