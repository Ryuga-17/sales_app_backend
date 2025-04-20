import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("SUPABASE_HOST"),
            dbname=os.getenv("SUPABASE_DB"),
            user=os.getenv("SUPABASE_USER"),
            password=os.getenv("SUPABASE_PASSWORD"),
            port=os.getenv("SUPABASE_PORT", 5432)
        )
        return conn
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return "Sales Management Backend is Running (Supabase Edition)"

@app.route('/api/orders', methods=['GET'])
def get_orders():
    db = get_db_connection()
    if isinstance(db, str):
        return jsonify({"error": db}), 500
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT o.id AS order_id, c.name AS customer_name, s.name AS salesperson_name, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN salespersons s ON o.salesperson_id = s.id
        """)
        orders = cursor.fetchall()
        return jsonify(orders)
    except Exception as e:
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
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

# Add more routes as needed following this structure

if __name__ == '__main__':
    app.run(debug=True)
