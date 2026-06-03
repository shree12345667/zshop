from flask import Blueprint, request, jsonify
from database import get_db

# Create a Blueprint (a separate modular app for products)
products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    db = get_db()
    # Order by id DESC so the newest additions show at the top of the shop
    products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    
    product_list = []
    for p in products:
        product_list.append({
            "id": p['id'], "name": p['name'], "brand": p['brand'], 
            "category": p['category'], "price": p['price'], 
            "size": p['size'], "warranty": p['warranty'],
            "payment": p['payment'], "image": p['image'], 
            "description": p['description']
        })
        
    # CRITICAL BUG FIX: Return the RAW array, not an object. 
    # This fixes the Javascript crash in shop.html and shop(after login).html!
    response = jsonify(product_list)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@products_bp.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    db = get_db()
    cursor = db.execute('''
        INSERT INTO products (name, brand, category, price, size, warranty, payment, image, description) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'), data.get('brand'), data.get('category'), 
        float(data.get('price', 0)), data.get('size'), data.get('warranty'),
        data.get('payment'), data.get('image'), data.get('description')
    ))
    db.commit()
    return jsonify({"success": True, "message": "Product added", "id": cursor.lastrowid}), 201

@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE products 
        SET name=?, brand=?, category=?, price=?, size=?, warranty=?, payment=?, image=?, description=? 
        WHERE id=?
    ''', (
        data.get('name'), data.get('brand'), data.get('category'), 
        float(data.get('price', 0)), data.get('size'), data.get('warranty'),
        data.get('payment'), data.get('image'), data.get('description'), product_id
    ))
    db.commit()
    return jsonify({"success": True, "message": "Product updated"})

@products_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id=?", (product_id,))
    db.commit()
    return jsonify({"success": True, "message": "Product deleted"})