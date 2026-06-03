from flask import Blueprint, jsonify
from database import get_db

# Create a Blueprint for customer management
customers_bp = Blueprint('customers_bp', __name__)

@customers_bp.route('/api/users', methods=['GET'])
def get_users():
    """Fetch all registered users for the Admin Dashboard"""
    db = get_db()
    try:
        # Fetch id, email, and role (Exclude passwords for security)
        users_rows = db.execute("SELECT id, email, role FROM users ORDER BY id DESC").fetchall()
        
        user_list = []
        for row in users_rows:
            user_list.append({
                "id": row['id'],
                "email": row['email'],
                "role": row['role']
            })
            
        return jsonify({"success": True, "users": user_list})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500