import sqlite3
import os

DATABASE = 'shop.db'

def get_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  
    return conn

def init_db(app):
    """Initialize the database with correct UI schemas."""
    with app.app_context():
        db = get_db()
        
        # Create Users Table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer'
            )
        ''')
        
        # Create Products Table (Matches your Admin Dashboard exactly)
        db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                price REAL NOT NULL,
                size TEXT,
                warranty TEXT,
                payment TEXT,
                image TEXT,
                description TEXT
            )
        ''')
        db.commit()