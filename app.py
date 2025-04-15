from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configure CORS: Allow only specific origins in production (for example)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
# For production, restrict origins like:
# CORS(app, resources={r"/api/*": {"origins": ["http://your-frontend-domain.com"]}})

def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="VIVEKs-MacBook-Air.local",
            user="root",
            password="Printer@17",
            database="sales_management"
        )
        if db.is_connected():
            return db
    except Error as e:
        return str(e)

@app.route('/')
def home():
    return "Sales Management Backend is Running"

@app.route('/api/orders', methods=['GET'])
def get_orders():
    db = get_db_connection()
    if isinstance(db, str):
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id AS order_id, c.name AS customer_name, s.name AS salesperson_name, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN salespersons s ON o.salesperson_id = s.id
        """)
        orders = cursor.fetchall()
        return jsonify(orders)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    db = get_db_connection()
    if isinstance(db, str):
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.name AS product, p.price, od.quantity, (p.price * od.quantity) AS total_price
            FROM order_details od
            JOIN products p ON od.product_id = p.id
            WHERE od.order_id = %s
        """, (order_id,))
        order_details = cursor.fetchall()
        return jsonify(order_details)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO products (name, category, price, stock)
            VALUES (%s, %s, %s, %s)
        """, (data['name'], data['category'], data['price'], data['stock']))
        db.commit()
        return jsonify({"message": "Product added successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_id, salesperson_id, order_date)
            VALUES (%s, %s, %s)
        """, (data['customer_id'], data['salesperson_id'], data['order_date']))
        order_id = cursor.lastrowid

        for item in data['products']:
            cursor.execute("""
                INSERT INTO order_details (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, item['product_id'], item['quantity']))
        db.commit()
        return jsonify({"message": "Order created successfully", "order_id": order_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/payments', methods=['POST'])
def add_payment():
    data = request.json
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO payments (order_id, payment_date, amount, payment_method)
            VALUES (%s, %s, %s, %s)
        """, (data['order_id'], data['payment_date'], data['amount'], data['payment_method']))
        db.commit()
        return jsonify({"message": "Payment recorded successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/shipments', methods=['POST'])
def add_shipment():
    data = request.json
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO shipments (order_id, shipped_date, carrier, tracking_number)
            VALUES (%s, %s, %s, %s)
        """, (data['order_id'], data['shipped_date'], data['carrier'], data['tracking_number']))
        db.commit()
        return jsonify({"message": "Shipment created successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/returns', methods=['POST'])
def add_return():
    data = request.json
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO returns (order_id, return_date, reason)
            VALUES (%s, %s, %s)
        """, (data['order_id'], data['return_date'], data['reason']))
        db.commit()
        return jsonify({"message": "Return processed successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()
@app.route('/api/products', methods=['GET'])
def get_products():
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        # Ensure price is float before sending to frontend
        for product in products:
            if 'price' in product:
                try:
                    product['price'] = float(product['price'])
                except (ValueError, TypeError):
                    product['price'] = 0.0  # fallback if invalid

        return jsonify(products)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

# Add these endpoints to your existing Flask app

@app.route('/api/customers', methods=['GET'])
def get_customers():
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        return jsonify(customers)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/salespersons', methods=['GET'])
def get_salespersons():
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM salespersons")
        salespersons = cursor.fetchall()
        return jsonify(salespersons)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    db = get_db_connection()
    if isinstance(db, str): 
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(dictionary=True)
        
        # Get total orders
        cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
        total_orders = cursor.fetchone()['total_orders']
        
        # Get total products
        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        total_products = cursor.fetchone()['total_products']
        
        # Calculate total revenue (simplified)
        cursor.execute("""
            SELECT SUM(p.price * od.quantity) as total_revenue
            FROM order_details od
            JOIN products p ON od.product_id = p.id
        """)
        result = cursor.fetchone()
        total_revenue = result['total_revenue'] if result['total_revenue'] else 0
        
        # Calculate average order value
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return jsonify({
            "total_orders": total_orders,
            "total_products": total_products,
            "total_revenue": total_revenue,
            "average_order_value": average_order_value
        })
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)