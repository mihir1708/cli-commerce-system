# System Overview

## Introduction

This is a command-line application for e-commerce shopping created using `SQLite` and `Python` where sales agents can view sales analytics and update product information, customers can browse products, place orders, and manage their shopping carts using the system.


### Core Components

1. **Database Layer (`db.py`)**
- Handles SQLite database connection
- Set up tables schema
- Optional : Demo data for testing (may or may not be there)

2. **Authentication (`auth.py`)**
- Handles user login with user id or email address
- New user registration
- Password validation
- Role-based access for `customer` and `sales` agent

3. **Session Management (`sessions.py`)**   
- Tracks customer sessions based on their browsing pattern
- Records session start and end times
- Records various activities to parent sessions like viewing product or adding product to cart

4. **Customer Module (`customer.py`)**
- Product search 
- Product detail viewing
- Shopping cart 
- Order placement and checkout
- Order history viewing

5. **Sales Agent Module (`sales.py`)**
- Product information updates i,e.. stock and price
- Weekly sales report
- Top products by views and order count report

6. **Main Application (`app.py`)**
- Entry point for the application to start its execution
- Handles re routing to various menus based on inputs and role 


## Database Schema

The following tables are used to store data:

- **users**(uid, pwd, role) – role ∈ {customer, sales}
- **customers**(cid, name, email)
- **products**(pid, name, category, price, stock_count, descr)
- **orders**(ono, cid, sessionNo, odate, shipping_address)
- **orderlines**(ono, lineNo, pid, qty, uprice)
- **sessions**(cid, sessionNo, start_time, end_time)
- **viewedProduct**(cid, sessionNo, ts, pid) --ts is the timestamp
- **search**(cid, sessionNo, ts, query)
- **cart**(cid, sessionNo, pid, qty)

## Data Flow

### Customer Flow

1. User logs in or registers
2. System starts a session
3. Customer searches for products
4. System records search queries and viewed products
5. Customer adds items to cart
6. Customer proceeds to checkout
7. System creates order and orderlines records
8. System updates product stock
9. Session ends on logout

### Sales Agent Flow

1. Agent logs in with credentials
2. Agent accesses sales menu
3. Agent can do the following:
   - View and update product details
   - Generate weekly sales reports
   - View top-performing products
4. System updates database accordingly
5. Session ends on logout

## Key Features

### For Customers
- Search prooducts by either name, category or description
- View product information
- Add or remove items from shopping cart
- Place orders with stock updates
- View order history

### For Sales Agents
- Update product prices
- Update product stock levels
- View weekly sales reports
- Vieww top products by orders and views

## Security

- Password-based authentication with masking
- Role-based access 
- SQL injection prevention:
  - We use `?` placeholders everywhere and never stitch user input directly into SQL.
  - We don’t build SQL with string concatenation, f-strings or `format()` when user data is involved.
  - When queries need to be dynamic like a keyword search in product search, we assemble the shape from safe pieces and pass values as bound parameters (e.g., `LIKE ?`)
  - We validate and normalize inputs for e.g., ensure IDs are numeric and compare emails case-insensitively with `lower(?)`
  - We enable foreign keys (`PRAGMA foreign_keys = ON`) to keep referential constraints.


