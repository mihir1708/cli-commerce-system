from datetime import datetime, timedelta


def sales_menu(conn):
    while True:
        print("\n == Sales Menu Page ==")
        print("1) View or update product")
        print("2) Weekly sales report")
        print("3) Top products by order and view counts")
        print("0) Logout")
        choice = input("Make a selection: ").strip()
        if choice == "1":
            sales_product_update(conn)
        elif choice == "2":
            weekly_sales_report(conn)
        elif choice == "3":
            top_products(conn)
        elif choice == "0":
            break
        else:
            print("Please make a valid selection")


def sales_product_update(conn):
    pid_s =input("Product ID: ").strip()
    
    if not pid_s.isdigit():
        print("Please enter a valid product ID")
        return
    
    pid=int(pid_s)
    cur = conn.cursor()
    product_id=(pid,)
    cur.execute('SELECT pid, name, category, price, stock_count, descr FROM products WHERE pid=?;', product_id)
    product = cur.fetchone()
    
    if product is None:
        print("This product does not exist")
        return
    
    print("\n{:<6} {:<20} {:<10} {:<10} {:<8}".format(
        "PID", "Name", "Category", "Price", "Stock"
    ))
    print("-" * 60)
    print("{:<6} {:<20} {:<10} ${:<9.2f} {:<8}".format(
        product['pid'], (product['name'] or '')[:20], (product['category'] or '')[:10],
        product['price'], product['stock_count']
    ))
    
    print("\nUpdate: \n1) Price\n2) Stock\n3) Cancel")
    sel = input("Choose: ").strip()
    
    if sel == "1":
        val = input("New price: ").strip()
        try:
            price = float(val)
            if price <= 0:
                print("Price cannot be negative")
                return
            update_params=(price, pid)
            conn.execute('UPDATE products SET price=? WHERE pid=?;', update_params)
            conn.commit()
            print("Price has been updated")
        except ValueError:
            print("Invalid input")
    elif sel == "2":
        val = input("New stock count: ").strip()
        if not val.isdigit():
            print("Stock must be a non-negative integer.")
            return
        
        stock = int(val)
        stock_params=(stock, pid)
        conn.execute('UPDATE products SET stock_count=? WHERE pid=?;', stock_params)
        conn.commit()
        print("Stock count has been updated")


def weekly_sales_report(conn):
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cur = conn.cursor()
    
    cutoff_param=(cutoff,)
    cur.execute('SELECT COUNT(DISTINCT o.ono) FROM orders o WHERE o.odate>=?;', cutoff_param)
    result = cur.fetchone()
    num_orders = result[0]
    
    cutoff_param=(cutoff,)
    cur.execute(
        '''
        SELECT COUNT(DISTINCT ol.pid)
        FROM orderlines ol 
        JOIN orders o ON ol.ono=o.ono
        WHERE o.odate>=?;
        ''',
        cutoff_param
    )
    result = cur.fetchone()
    num_products = result[0]
    
    cutoff_param=(cutoff,)
    cur.execute('SELECT COUNT(DISTINCT o.cid) FROM orders o WHERE o.odate>=?;', cutoff_param)
    result = cur.fetchone()
    num_customers = result[0]
    
    cutoff_param=(cutoff,)
    cur.execute(
        '''
        SELECT COALESCE(SUM(ol.qty * ol.uprice), 0)
        FROM orderlines ol JOIN orders o ON ol.ono=o.ono
        WHERE o.odate>=?;
        ''',
        cutoff_param
    )
    result = cur.fetchone()
    
    if result[0] is not None:
        total_sales = result[0]
    else:
        total_sales = 0.0
    
    if num_customers > 0:
        avg_per_customer = total_sales / num_customers
    else:
        avg_per_customer = 0.0
    
    print("\nLast week's sales report")
    print(f"Distinct orders: {num_orders}")
    print(f"Distinct products sold: {num_products}")
    print(f"Distinct customers: {num_customers}")
    print(f"Average dollar spent per customer: ${avg_per_customer:.2f}")
    print(f"Total sales: ${total_sales:.2f}")


def top_products(conn):
    cur = conn.cursor()
    
    print("\n-- Top 3 products by order counts --")
    cur.execute(
        '''
        SELECT ol.pid, p.name, COUNT(DISTINCT ol.ono) AS cnt
        FROM orderlines ol 
        JOIN products p ON ol.pid=p.pid
        GROUP BY ol.pid
        ORDER BY cnt DESC, ol.pid ASC;
        '''
    )
    all_rows = cur.fetchall()
    threshold = None
    if len(all_rows) <= 3:
        results = all_rows
    else:
        threshold = all_rows[2]['cnt']
        results = [r for r in all_rows if r['cnt'] >= threshold]
    print("\n{:<6} {:<30} {:<10}".format("PID", "Name", "Orders"))
    print("-" * 50)
    for row in results:
        print("{:<6} {:<30} {:<10}".format(row['pid'], (row['name'] or '')[:30], row['cnt']))
    
    print("\n-- Top 3 products by view counts --")
    cur.execute(
        '''
        SELECT v.pid, p.name, COUNT(*) AS cnt
        FROM viewedProduct v 
        JOIN products p ON v.pid=p.pid
        GROUP BY v.pid
        ORDER BY cnt DESC, v.pid ASC;
        '''
    )
    all_rows = cur.fetchall()
    if len(all_rows) <= 3:
        results = all_rows
    else:
        threshold = all_rows[2]['cnt']
        results = [r for r in all_rows if r['cnt'] >= threshold]
    print("\n{:<6} {:<30} {:<10}".format("PID", "Name", "Views"))
    print("-" * 50)
    for row in results:
        print("{:<6} {:<30} {:<10}".format(row['pid'], (row['name'] or '')[:30], row['cnt']))


