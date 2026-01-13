# User Guide

## Getting Started

### Running the Application

```bash
python app.py
```

> The database is initialized when you run the program at first

Run with a provided DB (e.g., TA test DB):

```bash
python app.py /path/to/prj-test.db
```

Notes
- For demos, use the TA DB: `python app.py prj-test.db`.
- Without an argument, the app uses/creates `ecommerce.db` (local).
- If the DB is empty, required tables are created.

## Creating an Account

1. Select option `2`  from main menu
2. Enter your valid credentials to continue
3. System creates your account based on the credentials
4. You are then logged in as a customer

## Logging In

1. Select option `1` from main menu
2. Enter your user ID or email address 
3. Enter your password
4. You will see either a customer menu or a sales menu depending on your role

# **Note:** Sales agent accounts are not created by signup. On the local default DB use: uid `1`, password `sales`. On the TA demo DB use the sales credentials in that DB.
- User ID: `1`
- Password: `sales`

## Customer Features

### Search Products

- Select option `1` from customer menu
- Type keywords to search either the name, category or description
- View results 5 at a time via pagination control
- Enter the product ID to see further details (as explained below)
- Enter `back` to return to customer memu

### View Product Details

- Takes place after entering product ID during search
- See full product details of the selected product
- Add to cart if you want to buy it

### Manage Cart

- Select option `2` from customer menu
- Displays all items in your cart
- Update quantity or remove items
- See the total price of the cart

### Checkout

- Select option `3` from customer menu
- System checks if enough stock is available
- Order is created if stock doesn't drop to negative after the order
- Cart is reset after a successful checkout
- Stock is reduced automatically to reflect the change

### View Order History

- Select option `4` from customer menu
- Displays your order history
- Enter order number to further view order details

## Sales Agent Features

### Update Product

- Select option `1` from sales menu
- Enter the desired product ID
- Choice to update price or stock of the selected product
- Enter a new value (price or stock count)
- Changes are reflected immediately in the tables

### Weekly Sales Report

- Select option `2` from sales menu
- View statistics for last 7 days of the following:
  - Number of orders
  - Number of products sold
  - Number of customers
  - Average dollar amount spent per customer
  - Total sales overall

### Top Products

- Select option `3` from sales menu
- See top 3 products by number of orders
- See top 3 products by number of views


