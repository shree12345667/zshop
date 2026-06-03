from flask import Blueprint, request, jsonify
import sqlite3
import json

# Create a Blueprint so we can easily plug this into your main app.py
orders_bp = Blueprint('orders_bp', __name__)
DATABASE = 'shop.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_orders_table():
    db = get_db()
    # Store orders natively. Items are stored as a JSON string for flexibility.
    db.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            customer TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            total TEXT NOT NULL,
            status TEXT NOT NULL,
            promo TEXT,
            items TEXT NOT NULL
        )
    ''')
    db.commit()

# Initialize the table when this file is run
init_orders_table()

@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    """Fetch all orders for the Admin Dashboard"""
    db = get_db()
    orders_rows = db.execute("SELECT * FROM orders ORDER BY rowid DESC").fetchall()
    
    orders = []
    for row in orders_rows:
        orders.append({
            "id": row['id'],
            "date": row['date'],
            "customer": row['customer'],
            "email": row['email'],
            "address": row['address'],
            "total": row['total'],
            "status": row['status'],
            "promo": row['promo'],
            "items": json.loads(row['items']) # Convert JSON string back to Python list
        })
    return jsonify({"success": True, "orders": orders})

@orders_bp.route('/api/orders', methods=['POST'])
def create_order():
    """Receive a new order from shop(after login).html"""
    data = request.json
    db = get_db()
    
    try:
        db.execute('''
            INSERT INTO orders (id, date, customer, email, address, total, status, promo, items)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('id'),
            data.get('date'),
            data.get('customer'),
            data.get('email', ''),
            data.get('address'),
            data.get('total'),
            data.get('status', 'AWAITING PAYMENT'),
            data.get('promo', ''),
            json.dumps(data.get('items', [])) # Convert Python list to JSON string for DB
        ))
        db.commit()
        return jsonify({"success": True, "message": "Order saved securely to database"})
    except sqlite3.IntegrityError:
        # If order ID already exists, update its status (useful for payment success overrides)
        db.execute("UPDATE orders SET status = ? WHERE id = ?", (data.get('status'), data.get('id')))
        db.commit()
        return jsonify({"success": True, "message": "Order updated securely"})

@orders_bp.route('/api/orders/<order_id>', methods=['PUT'])
def update_order_status(order_id):
    """Allow Admin to update status to SHIPPED or CANCELLED"""
    data = request.json
    new_status = data.get('status')
    
    db = get_db()
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    db.commit()
    return jsonify({"success": True, "message": f"Order {order_id} marked as {new_status}"})