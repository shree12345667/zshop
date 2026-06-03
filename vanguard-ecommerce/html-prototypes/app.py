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
app.register_blueprint(customers_bp, url_prefix='/api') 

# Force the database to build immediately outside the main block so Railway sees it
if not os.path.exists(DATABASE):
    print("Database missing. Initializing new schema...")
    init_db(app)

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
    return jsonify({"success": True, "message": "Analytics endpoint active and waiting for data."})

@app.route('/api/discounts', methods=['GET'])
def get_discounts():
    """Future endpoint for discounts.html"""
    return jsonify({"success": True, "message": "Discounts endpoint active and waiting for data."})

# --- RAILWAY UNLOCK (0.0.0.0 binds it to the public internet) ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
