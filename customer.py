from datetime import datetime

# Records a search query in the database
def record_search(conn, cid, session_no, query):
    now_dt = datetime.now()
    timestamp = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    search_insert_params = (cid, session_no, timestamp, query)
    conn.execute(
        "INSERT INTO search(cid, sessionNo, ts, query) VALUES(?,?,?,?)",
        search_insert_params
    )
    conn.commit()


# Records a product view in the database
def record_view(conn, cid, session_no, pid):
    now_dt = datetime.now()
    timestamp = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    view_insert_params = (cid, session_no, timestamp, pid)
    conn.execute(
        "INSERT INTO viewedProduct(cid, sessionNo, ts, pid) VALUES(?,?,?,?)",
        view_insert_params
    )
    conn.commit()


# Searches for products in the database based on a keyword
def customer_search(conn, cid, session_no):
    
    # get keywords (space-separated) from the user
    raw = input("==> Keywords (space-separated): ").strip()
    if not raw:
        print("Empty keyword.")
        return
    keywords = raw.lower().split()
    # record the original search string
    record_search(conn, cid, session_no, raw)
    
    # Build AND semantics across keywords (case-insensitive)
    # Single keyword: match in name OR description
    # Multiple keywords: require each keyword to appear in either name OR description
    params = []
    if len(keywords) == 1:
        like_kw = f"%{keywords[0]}%"
        where_sql = "(lower(name) LIKE ? OR lower(descr) LIKE ?)"
        params = [like_kw, like_kw]
    else:
        parts = []
        for kw in keywords:
            like_kw = f"%{kw}%"
            parts.append("(lower(name) LIKE ? OR lower(descr) LIKE ?)")
            params.extend([like_kw, like_kw])
        where_sql = " AND ".join(parts)
    sql = f"""
        SELECT pid, name, category, price, stock_count
        FROM products
        WHERE {where_sql}
        ORDER BY pid
    """
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    
    # get the results from the database
    results = cur.fetchall()
    
    # if no results are found, print an error message and return
    if not results:
        print("No products found.")
        return
    
    # Pagination =======================================================
    
    # initialize the page number
    page = 0
    
    # Main Loop
    while True:
        
        # calculate the start and end indices for the current page
        start = page * 5
        end = start + 5
        page_items = results[start:end]
        
        # if there are no more results, print an error message and break the loop
        if not page_items:
            print("No more results.")
            break
        
        # print the results for the current page
        print(f"\n-- Results Page {page + 1} --\n")
        # Print header row
        print("\n{:<3} {:<6} {:<20} {:<10} {:<10} {:<8}".format(
            "#", "PID", "Name", "Category", "Price", "Stock"
        ))
        print("-" * 60)
        
        # Print each product row
        for i, r in enumerate(page_items, start=1):
            displayed_index = start + i
            print("{:<3} {:<6} {:<20} {:<10} ${:<9.2f} {:<8}".format(
                f"{displayed_index})", r['pid'], (r['name'] or '')[:20], (r['category'] or '')[:10],
                r['price'], r['stock_count']
            ))
        
        # print the navigation options
        print("\nChoose from the following options:")
        print("n) Next page\np) Prev page\nb) Back")
        print("or enter the index of the product you want to add/view:")
        
        # get the user's choice
        selection = input("Choose: ").strip().lower()
        
        # Handle navigation options
        if selection == "n":
            page += 1
        elif selection == "p":
            page = max(0, page - 1)
        elif selection == "b":
            break
        elif selection.isdigit():
            index = int(selection)
            if 1 <= index <= len(page_items):
                pid = page_items[index - 1]["pid"]
                product_detail(conn, cid, session_no, pid)
            elif (start + 1) <= index <= (start + len(page_items)):
                pid = page_items[index - start - 1]["pid"]
                product_detail(conn, cid, session_no, pid)
            else:
                print("Invalid selection.")
        else:
            print("Invalid input.")


# Displays the details of a product and allows the user to add it to the cart
def product_detail(conn, cid, session_no, pid):
    cur = conn.cursor()
    pid_param = (pid,)
    cur.execute(
        "SELECT pid, name, category, price, stock_count, descr FROM products WHERE pid = ?",
        pid_param
    )
    
    # get the product details from the database
    r = cur.fetchone()
    if not r:
        print("Product not found.")
        return
    
    # record the view of the product in the database
    record_view(conn, cid, session_no, pid)
    
    # print the product details
    print(
        f"\nPID {r['pid']}\nName: {r['name']}\nCategory: {r['category']}\nPrice: ${r['price']:.2f}\nStock: {r['stock_count']}\nDesc: {r['descr']}"
    )
    
    # if the product is in stock, ask the user if they want to add it to the cart
    if r["stock_count"] > 0:
        ans = input("Add to cart (qty 1)? [y/N]: ").strip().lower().replace(" ", "")
        
        # if the user wants to add the product to the cart, add it to the cart
        if ans == "y":
            add_to_cart(conn, cid, session_no, pid, 1)
    else:
        print("Out of stock.")


def add_to_cart(conn, cid, session_no, pid, qty):
    cur = conn.cursor()
    
    # get the stock count of the product from the database
    pid_param_stock = (pid,)
    cur.execute("SELECT stock_count FROM products WHERE pid = ?", pid_param_stock)
    
    # if the product does not exist, print an error message and return
    row = cur.fetchone()
    if not row:
        print("Product does not exist.")
        return
    
    # get the stock count of the product from the database
    stock = row[0]
    
    # get the quantity of the product in the cart from the database
    cart_check_params = (cid, session_no, pid)
    cur.execute("SELECT qty FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?", cart_check_params)
    
    # if the product is already in the cart, add the quantity to the existing quantity
    existing_product = cur.fetchone()
    new_qty = qty
    if existing_product:
        new_qty = existing_product[0] + qty
    if new_qty > stock:
        print("Insufficient stock.")
        return
    if existing_product:
        # update the quantity of the product already in the cart
        update_cart_params = (new_qty, cid, session_no, pid)
        cur.execute(
            "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?",
            update_cart_params
        )
    else:
        # add the product to the cart if it is not already in the cart
        insert_cart_params = (cid, session_no, pid, qty)
        cur.execute(
            "INSERT INTO cart(cid, sessionNo, pid, qty) VALUES(?,?,?,?)",
            insert_cart_params
        )
    # commit the changes to the database
    conn.commit()
    print("Product added to cart.")



# Displays the cart of the user
def customer_cart(conn, cid, session_no):
    
    # get the items in the cart from the database
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.pid, c.qty, p.name, p.category, p.price, p.stock_count, p.descr
        FROM cart c JOIN products p ON c.pid = p.pid
        WHERE c.cid = ? AND c.sessionNo = ?
        ORDER BY p.pid
        """,
        (cid, session_no),
    )
    items = cur.fetchall()
    
    # if the cart is empty, print message and return to main menu
    if not items:
        print("\nThe cart is empty.")
        return
    
    # Main Loop - only runs if cart has items
    while True:
        
        # Refresh cart items in case they were updated
        cur.execute(
            """
            SELECT c.pid, c.qty, p.name, p.category, p.price, p.stock_count, p.descr
            FROM cart c JOIN products p ON c.pid = p.pid
            WHERE c.cid = ? AND c.sessionNo = ?
            ORDER BY p.pid
            """,
            (cid, session_no),
        )
        items = cur.fetchall()
        
        # print the header row
        print("\nThe cart contains the following items:")
        print("\n{:<3} {:<6} {:<20} {:<10} {:<10} {:<10} {:<50}".format(
            "#", "PID", "Name", "Category", "Price", "Stock", "Descr"
        ))
        print("-" * 80)
        
        # print each item in the cart
        for i, it in enumerate(items, start=1):
            print("{:<3} {:<6} {:<20} {:<10} ${:<9.2f} {:<10} {:<8}".format(
                f"{i})", it['pid'], it['name'][:20], it['category'][:10], it['price'], it['stock_count'], (it['descr'] or '')[:50]
            ))
            
        # print the navigation options
        print("\nChoose from the following options:")
        print("u) Update qty\nr) Remove item\nc) Checkout\nb) Back")
        selection = input("Choose: ").strip().lower().replace(" ", "")
        
        # Handle update quantity option
        if selection == "u":
            
            # get the item number from the user
            index = input("Item number: ").strip()
            if not index.isdigit():
                print("Invalid number.")
                continue
            index = int(index)
            
            # if the item number is out of range, print an error message and continue the loop
            if index < 1 or index > len(items):
                print("Out of range.")
                continue
            
            # get the new quantity from the user
            new_quantity = input("New quantity: ").strip()
            if not new_quantity.isdigit():
                print("Quantity must be positive integer.")
                continue
            
            # convert the new quantity to an integer
            new_quantity = int(new_quantity)
            if new_quantity <= 0:
                print("Quantity must be positive.")
                continue
            
            # get the product id and stock count of the item
            pid = items[index - 1]["pid"]
            stock = items[index - 1]["stock_count"]
            
            # if the new quantity exceeds the available stock, print an error message and continue the loop
            if new_quantity > stock:
                print("Exceeds available stock.")
                continue
            
            # update the quantity of the item in the cart
            conn.execute(
                "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?",
                (new_quantity, cid, session_no, pid),
            )
            # commit the changes to the database
            conn.commit()
            
        # Handle remove item option
        elif selection == "r":
            
            # get the item number from the user
            index = input("Item number: ").strip()
            if not index.isdigit():
                print("Invalid number.")
                continue
            index = int(index)
            if index < 1 or index > len(items):
                print("Out of range.")
                continue
            pid = items[index - 1]["pid"]
            
            # delete the item from the cart
            conn.execute(
                "DELETE FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?",
                (cid, session_no, pid),
            )
            # commit the changes to the database
            conn.commit()
            
        # Handle checkout option
        elif selection == "c":
            # get the shipping address from the user
            address = input("Shipping address: ").strip()
            
            # if the shipping address is empty, print an error message and continue the loop
            if not address:
                print("Address required.")
                continue
            
            # get the confirmation from the user
            confirmation = input("Place order? [y/N]: ").strip().lower().replace(" ", "")
            
            # if the user wants to place the order, place the order
            if confirmation == "y":
                place_order(conn, cid, session_no, address)
                
        # Handle back option
        elif selection == "b":
            break
        else:
            print("Invalid choice.")


# Places an order in the database
def place_order(conn, cid, session_no, address):
    cur = conn.cursor()
    
    # get the items in the cart from the database
    cur.execute(
        "SELECT c.pid, c.qty, p.price, p.stock_count FROM cart c JOIN products p ON c.pid = p.pid WHERE c.cid = ? AND c.sessionNo = ?",
        (cid, session_no),
    )
    items = cur.fetchall()
    
    # if the cart is empty, print an error message and return
    if not items:
        print("Cart is empty.")
        return
    
    # check if the quantity of the items in the cart exceeds the available stock
    for it in items:
        if it["qty"] > it["stock_count"]:
            print(f"Insufficient stock for PID {it['pid']}.")
            return
    try:
        # fetch the maximum order number from the database and ensure uniqueness
        cur.execute("SELECT MAX(ono) FROM orders")
        row = cur.fetchone()
        
        if row and row[0] is not None:
            ono = row[0] + 1
        else:
            ono = 1
        
        odate = datetime.now().strftime("%Y-%m-%d")
        order_insert_params = (ono, cid, session_no, odate, address)
        cur.execute(
            "INSERT INTO orders(ono, cid, sessionNo, odate, shipping_address) VALUES(?,?,?,?,?)",
            order_insert_params,
        )
        line_no = 1
        # calculate the total price of the order
        total = 0.0
        # insert the items into the orderlines table
        for it in items:
            # get the product id, quantity, and price of the item
            pid = it["pid"]
            qty = it["qty"]
            price = it["price"]
            total += qty * price
            # insert the item into the orderlines table
            cur.execute(
                "INSERT INTO orderlines(ono, lineNo, pid, qty, uprice) VALUES(?,?,?,?,?)",
                (ono, line_no, pid, qty, price),
            )
            line_no += 1
            # update the stock count of the product
            cur.execute(
                "UPDATE products SET stock_count = stock_count - ? WHERE pid = ?",
                (qty, pid),
            )
        # delete the items from the cart
        cur.execute("DELETE FROM cart WHERE cid = ? AND sessionNo = ?", (cid, session_no))
        # commit the changes to the database
        conn.commit()
        print(f"Order {ono} placed. Total ${total:.2f}")
    except Exception as e:
        # rollback the transaction if an error occurs
        conn.rollback()
        print("Checkout failed:", e)


# Displays the orders of the user
def customer_orders(conn, cid):
    
    # get the orders from the database
    cur = conn.cursor()
    cur.execute(
        """
        SELECT o.ono, o.odate, o.shipping_address, COALESCE(SUM(ol.qty * ol.uprice), 0) AS total
        FROM orders o LEFT JOIN orderlines ol ON o.ono = ol.ono
        WHERE o.cid = ?
        GROUP BY o.ono
        ORDER BY o.odate DESC
        """,
        (cid,),
    )
    orders = cur.fetchall()
    
    # if there are no orders, print an error message and return
    if not orders:
        print("No orders.")
        return
    
    # initialize the page number
    page = 0
    
    # Main Loop
    while True:
        start = page * 5
        end = start + 5
        page_items = orders[start:end]
        if not page_items:
            print("No more.")
            break
        print(f"\n== Orders Page {page + 1} ==\n")
        # table header
        print("\n{:<3} {:<6} {:<12} {:<30} {:<10}".format("#", "ONO", "Date", "Address", "Total"))
        print("-" * 70)
        # print each order
        for i, o in enumerate(page_items, start=1):
            addr = (o['shipping_address'] or '')[:30]
            date_str = (o['odate'] or '')
            ono_val = o['ono'] if o['ono'] is not None else 0
            total_val = o['total'] if o['total'] is not None else 0.0
            print("{:<3} {:<6} {:<12} {:<30} ${:<9.2f}".format(
                f"{i})", int(ono_val), date_str, addr, float(total_val)
            ))
            
        # print the navigation options
        print("n) Next\np) Prev\nb) Back")
        print("or enter the index of the order to view details:")
        selection = input("Choose: ").strip().lower().replace(" ", "")
        
        # Handle navigation options
        if selection == "n":
            page += 1
        elif selection == "p":
            page = max(0, page - 1)
        elif selection == "b":
            break
        elif selection.isdigit():
            index = int(selection)
            if 1 <= index <= len(page_items):
                show_order_details(conn, page_items[index - 1]["ono"])
            else:
                print("Invalid selection.")
        else:
            print("Invalid input.")


# Displays the details of an order
def show_order_details(conn, ono):
    cur = conn.cursor()
    
    # get the order details from the database
    cur.execute("SELECT ono, odate, shipping_address FROM orders WHERE ono = ?", (ono,))
    o = cur.fetchone()
    if not o:
        print("Order not found.")
        return
    
    # get the order lines from the database
    cur.execute(
        """
        SELECT ol.lineNo, p.name, p.category, ol.qty, ol.uprice, (ol.qty * ol.uprice) AS line_total
        FROM orderlines ol JOIN products p ON ol.pid = p.pid
        WHERE ol.ono = ?
        ORDER BY ol.lineNo
        """,
        (ono,),
    )
    lines = cur.fetchall()
    
    # print the order details
    print(f"\nOrder {o['ono']} | {o['odate']} | {o['shipping_address']}")
    
    # calculate the grand total and print table in consistent format
    grand = 0.0
    
    # print the table header
    print("\n{:<3} {:<20} {:<12} {:>5} {:>8} {:>10}".format("#", "Name", "Category", "Qty", "Unit", "Line"))
    print("-" * 65)
    # print each order line
    for i, ln in enumerate(lines, start=1):
        # get the name, category, quantity, unit price, and line total of the order line
        name = (ln['name'] or '')[:20]
        category = (ln['category'] or '')[:12]
        qty = ln['qty'] if ln['qty'] is not None else 0
        uprice = float(ln['uprice']) if ln['uprice'] is not None else 0.0
        line_total = float(ln['line_total']) if ln['line_total'] is not None else (qty * uprice)
        # print the order line
        print("{:<3} {:<20} {:<12} {:>5} ${:>7.2f} ${:>9.2f}".format(
            f"{i})", name, category, qty, uprice, line_total
        ))
        grand += line_total
    # print the grand total
    print(f"\nGrand total: ${grand:.2f}")



# Displays the customer menu
def customer_menu(conn, cid, session_no):
    
    # Main Loop
    while True:
        print(f"\n=== Customer Menu (CID {cid}, Session {session_no}) ===")
        print("1) Search products")
        print("2) View cart")
        print("3) My orders")
        print("0) Logout")
        choice = input("Choose: ").strip().replace(" ", "")
        
        # Handle search products option
        if choice == "1":
            customer_search(conn, cid, session_no)
        elif choice == "2":
            customer_cart(conn, cid, session_no)
        elif choice == "3":
            customer_orders(conn, cid)
        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid choice.")


