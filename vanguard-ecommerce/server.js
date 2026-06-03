const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();
const PORT = 3000;
const SECRET_KEY = 'vanguard_super_secret_key_change_in_production'; 

app.use(express.json());
app.use(cors()); 

// 1. Database Setup (Now with a 'cart' column!)
const db = new sqlite3.Database('./vanguard.db', (err) => {
    if (err) {
        console.error('Error connecting to DB:', err.message);
    } else {
        console.log('✅ Connected to SQLite database.');
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            cart TEXT DEFAULT '[]',
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )`, () => {
            // Safely upgrade existing databases to include the cart column
            db.run(`ALTER TABLE users ADD COLUMN cart TEXT DEFAULT '[]'`, () => {});
        });
    }
});

// 2. REGISTER ENDPOINT
app.post('/api/register', async (req, res) => {
    const { fullName, email, password } = req.body;
    if (!fullName || !email || !password) return res.status(400).json({ error: 'All fields required.' });

    try {
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        const sql = `INSERT INTO users (fullName, email, password) VALUES (?, ?, ?)`;
        
        db.run(sql, [fullName, email, hashedPassword], function(err) {
            if (err) {
                if (err.message.includes('UNIQUE')) return res.status(400).json({ error: 'Email already exists.' });
                return res.status(500).json({ error: 'Database error.' });
            }
            const token = jwt.sign({ id: this.lastID }, SECRET_KEY, { expiresIn: '24h' });
            res.status(201).json({ message: 'User created.', token });
        });
    } catch (error) { res.status(500).json({ error: 'Server error.' }); }
});

// 3. LOGIN ENDPOINT
app.post('/api/login', (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ error: 'Required fields.' });

    db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
        if (err || !user) return res.status(401).json({ error: 'Invalid credentials.' });

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(401).json({ error: 'Invalid credentials.' });

        const token = jwt.sign({ id: user.id }, SECRET_KEY, { expiresIn: '24h' });
        res.status(200).json({ message: 'Login successful.', token });
    });
});

// 4. GET CURRENT USER & CART
app.get('/api/me', (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Not authenticated.' });

    jwt.verify(token, SECRET_KEY, (err, decoded) => {
        if (err) return res.status(403).json({ error: 'Token invalid.' });

        // Fetch User and their Cart from SQL!
        db.get(`SELECT fullName, email, cart FROM users WHERE id = ?`, [decoded.id], (dbErr, user) => {
            if (dbErr || !user) return res.status(404).json({ error: 'User not found.' });
            
            let parsedCart = [];
            try { parsedCart = JSON.parse(user.cart || '[]'); } catch(e) {}

            res.status(200).json({ 
                user: { fullName: user.fullName, email: user.email, cart: parsedCart } 
            });
        });
    });
});

// 5. SAVE CART TO DATABASE
app.post('/api/cart', (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Not authenticated.' });

    jwt.verify(token, SECRET_KEY, (err, decoded) => {
        if (err) return res.status(403).json({ error: 'Token invalid.' });

        const cartStr = JSON.stringify(req.body.cart || []);
        db.run(`UPDATE users SET cart = ? WHERE id = ?`, [cartStr, decoded.id], (dbErr) => {
            if (dbErr) return res.status(500).json({ error: 'Failed to save cart.' });
            res.status(200).json({ message: 'Cart saved to SQL.' });
        });
    });
});

app.listen(PORT, () => console.log(`🚀 Server running on http://localhost:${PORT}`));