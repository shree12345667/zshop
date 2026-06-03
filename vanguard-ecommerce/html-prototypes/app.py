from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

# Import modular scripts (Current Files)
from database import init_db, get_db, DATABASE
from routes_products import products_bp
from orders import orders_bp
from customers import customers_bp

app = Flask(__name__)
CORS(app) 

# Register the separated scripts with the correct /api prefix
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(customers_bp, url_prefix='/api') # <-- Customers linked here!

# --- AUTH ROUTES ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
    
    if user:
        return jsonify({
            "success": True, 
            "user": {"id": user['id'], "email": user['email'], "role": user['role']}
        })
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    db = get_db()
    try:
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        db.commit()
        return jsonify({"success": True, "message": "Account created!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email exists"}), 400

# --- UPCOMING FILES PREPARATION (Analytics & Discounts) ---
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Future endpoint for Analytics.html"""
    # We will build out this logic when we do the Analytics dashboard
    return jsonify({"success": True, "message": "Analytics endpoint active and waiting for data."})

@app.route('/api/discounts', methods=['GET'])
def get_discounts():
    """Future endpoint for discounts.html"""
    # We will build out this logic when we do the Discounts dashboard
    return jsonify({"success": True, "message": "Discounts endpoint active and waiting for data."})


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print("Database missing. Initializing new schema...")
    init_db(app)
    print("Modular Backend running on zshop-production-5704.up.railway.app")
    app.run(debug=True, port=5000)
