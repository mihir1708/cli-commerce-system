# Software Design

## Overview

Six major modules make up the application, each of which is responsible for particular tasks. Together, the modules provides us with a comprehensive e-commerce system with features for both customers and sales agents.

## Module Design

### 1. Database Module (`db.py`)

#### Responsibility
Sets up and initializes the SQLite database with all required tables and demo data.

#### Primary Functions

**`init_db(conn)`**
- **Purpose**: Creates all database tables (9 of them) if they don't exist already due to previous runs
- **Input**: Database connection object
- **Output**: None
- **What it does**: Creates table for all the 9 tables specified in the project description namely: users, customers, products, orders, orderlines, sessions, viewedProduct, search and cart


#### Relationships
- Called by `app.py` on startup
- Queried by all other m,odules

---

### 2. Authentication Module (`auth.py`)

#### Responsibility
Handles user login and new account creation with credential validation and password hashing.

#### Primary Functions

**`login(conn)`**
- **Purpose**: Authenticates existing users
- **Input**: Database connection object
- **Output**: Returns user ID and role (customer or sales) if successful
- **What it does**: Accepts a valid user ID or an email address with the password (masked when prompted). The entered password is hashed using SHA-256 and the hash is compared against the stored hash in the `users` table. If it matches, returns the user ID and role.

**`signup(conn)`**
- **Purpose**: Creates new customer accounts
- **Input**: Database connection object
- **Output**: Returns user ID and role if successful
- **What it does**: Gathers the user's name, email, phone number, and password before determining whether the email address is already in the system. The password is hashed using SHA-256 and only the hash is stored i,e.. no plaintext. A new user ID is generated and entries are made in the `users` and `customers` tables if the email is unique. When a new signup occurs, the role is always set to customer.

**`generate_user_id(conn)`**
- **Purpose**: Creates unique user IDs
- **Input**: Database connection object
- **Output**: String representing the user ID for the new user
- **What it does**: Finds the maximum existing user ID in the database and adds 1 to generate a new unique identifier for the new user.

#### Relationships
- Called by `app.py` in the main menu
- Creates records in `users` and `customers` tables
- Provides user credentials to determine menu access

---

### 3. Session Management Module (`sessions.py`)

#### Responsibility
Tracks customer activity by managing browsing sessions.

#### Primary Functions

**`start_session(conn, cid)`**
- **Purpose**: Begins a new session when customer logs in
- **Input**: Database connection and customer ID
- **Output**: Session number 
- **What it does**: The function tracks all of the customer's activities during this login by determining the highest session number for the customer, creating a new session with an incremented number, recording the start time, and returning the session number.

**`end_session(conn, cid, session_no)`**
- **Purpose**: Closes session when customer logs out
- **Input**: Database connection, customer ID and the session number
- **Output**: None
- **What it does**: When the customer logs out, this function updates the session record with the current time.

#### Relationships
- Called by `app.py` when customer logs in or logs out or creates an account
- Session numbers are used by `customer.py` to track customer activities

---

### 4. Customer Module (`customer.py`)

#### Responsibility
Implements all customer features including product browsing, cart management and order placement.

#### Primary Functions

**`customer_menu(conn, uid, session_no)`**
- **Purpose**: Main menu interface for customers to interact and navigate themselves with.
- **Input**: Database connection, user ID and session number
- **Output**: None
- **What it does**: Depending on the user's selection, this function directs them to the relevant function after displaying the customer menu options.

**`search_products(conn, cid, session_no)`**
- **Purpose**: Lets the customer search for products
- **Input**: Database connection, customer ID and session number
- **Output**: None
- **What it does**: The function enters a user-provided search term into the search table.  After that, it looks for products with the keyword in the name, category, or description. Five results are shown at once.  Entering a product ID allows users to view product details, and pagination allows them to view more results.

**`view_product_detail(conn, pid, cid, session_no)`**
- **Purpose**: Displays the entire information about a product as requested by the custromer
- **Input**: Database connection, product ID, customer ID and session number
- **Output**: None
- **What it does**: This function logs the view in the viewedProduct table for analytics purposes and shows the complete product details. The customer is then given the choice to put the item in their shopping cart.

**`view_cart(conn, cid, session_no)`**
- **Purpose**: Displays and manages the shopping cart
- **Input**: Database connection, customer ID and session number
- **Output**: None
- **What it does**: The function lists every item that is currently present in the cart, together with its cost and quantity. Customers can set quantity to 0 to remove items or update quantities. At the end, the total value of the cart is determined and shown.

**`checkout(conn, cid, session_no)`**
- **Purpose**: Completes the purchase and creates order and its history
- **Input**: Database connection, customer ID and session number
- **Output**: None
- **What it does**: First, the function confirms that there is enough inventory for every item in the cart. A new order record is created, orderline records are generated for each item in the cart, product stock counts are lowered appropriately and the cart is emptied if there is sufficient stock. It shows an error message and preserves the cart if there is not enough stock for any item.

**`view_orders(conn, cid)`**
- **Purpose**: Displays order history
- **Input**: Database connection and customer ID
- **Output**: None
- **What it does**: This function provides the customer with a list of all previous orders, including order dates and totals. To access the specific line items and products that are part of an order, customers can select a particular order number.

#### Relationships
- Called by `app.py` when customer logs in
- Uses session number from `sessions.py`
- Reads from and writes to the tables defined in `db.py` as the customer continues to perform various activities

---

### 5. Sales Agent Module (`sales.py`)

#### Responsibility
Provides sales agent tools for product management and reporting.

#### Primary Functions

**`sales_menu(conn)`**
- **Purpose**: Provides the main menu interface for sales agents
- **Input**: Database connection
- **Output**: None
- **What it does**: This function shows the menu options for the sales agent and depending on what the agent chooses, it directs them to the relevant step (or function).

**`sales_product_update(conn)`**
- **Purpose**: Updates product information
- **Input**: Database connection
- **Output**: None
- **What it does**: The function shows the most recent product details after receiving a product ID from the user. With correct validation, the agent can then update the price or stock count. The modifications are then saved to the products table after validation.

**`weekly_sales_report(conn)`**
- **Purpose**: Generates sales statistics for last 7 days
- **Input**: Database connection
- **Output**: None
- **What it does**: The function calculates a cutoff date of 7 days ago and queries the database for the number of distinct orders, distinct products sold, distinct customers and total sales revenue within this period. It then calculates the average spending per customer and displays all these statistics in a formatted report.

**`top_products(conn)`**
- **Purpose**: Shows best performing products
- **Input**: Database connection
- **Output**: None
- **What it does**: The function displays the top 3 distinct products by order count and by view count including the relevant product details

#### Relationships
- Called by `app.py` when sales agent logs in
- Uses session number from `sessions.py`
- Reads from and writes to the tables defined in `db.py` as the customer continues to perform various activities

---

### 6. Main Application Module (`app.py`)

#### Responsibility
Entry point that orchestrates the entire application flow.

#### Primary Functions

**`main()`**
- **Purpose**: To manage all the other modules and call required functions as needed
- **Input**: None
- **Output**: None
- **What it does**: This function mainly establishes the database connection, calls functions in `db.py` to configure the tables at start and fill in the test data. Following that, it starts the main menu loop, which displays options for signup and login, handles authentication, and directs users to the sales or customer menus according to their roles. It controls client sessions by initiating them upon login and terminating them upon logout. 

#### Relationships
- Coordinates with all other modules
- Creates database connection used by all functions

---

## Data Flow Between Modules

### Customer POV
1. `app.py` calls `auth.login()` or `auth.signup()` based on the action
2. `auth` module validates the provided credentials and returns user info to `app.py` for further processing
3. `app.py` calls `sessions.start_session()` for customers to record their session info
4. `app.py` calls `customer.customer_menu()` with session info
5. `customer` module records the activities with session number of the user
6. Customer actions update database tables accordingly
7. `app.py` calls `sessions.end_session()` upon logout and return to the main menu

### Sales Agent POV
1. `app.py` calls `auth.login()`
2. `auth` module validates provided credentials and returns the role "sales"
3. `app.py` calls `sales.sales_menu()` with the session info
4. `sales` module functions query and update database
5. `app.py` calls `sessions.end_session()` upon logout and returns to the main menu

### Database Initialization
1. `app.py` creates the database connection
2. `app.py` calls `db.init_db()` to create tables


## Key Design Decisions

### Modularity
Every module manages a single functional area.

### Database Connection 
In `app.py`, the database connection is created once and then passed to every function. By doing this, we make sure that every operation uses the same connection and transaction context.

### Session Tracking
Customer sessions tracks all the activities of the user namely searching products, viewing products, adding products to cart and finalizing the order in the same session.

### Role-Based Routing
After logging in, the system verifies the user's role and guides them to the relevant menu..

### Input Validation
Prior to database operations, every function verifies user input. By doing this, mistakes are avoided and data integrity is guaranteed.

### Parameterized Queries & SQL Injection
Most database query makes use of parameter binding  with ? placeholders. This maintains security and stops SQL injection attacks.
 
### Password Hashing
- User passwords are never stored in plaintext. We hash passwords using SHA-256 at signup and verify by comparing hashes at login.