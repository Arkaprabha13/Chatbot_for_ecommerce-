import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_path='ecommerce.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                stock_quantity INTEGER DEFAULT 0,
                brand TEXT,
                rating REAL DEFAULT 0.0,
                image_url TEXT,
                specifications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()

class User:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, username, email, password):
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        return None

class Product:
    def __init__(self, db):
        self.db = db
    
    def search_products(self, query, category=None, min_price=None, max_price=None, limit=20):
        """Search products based on query and filters"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        sql = '''
            SELECT id, name, category, price, description, stock_quantity, 
                   brand, rating, image_url, specifications
            FROM products WHERE 1=1
        '''
        params = []
        
        if query:
            sql += ' AND (name LIKE ? OR description LIKE ? OR brand LIKE ?)'
            search_term = f'%{query}%'
            params.extend([search_term, search_term, search_term])
        
        if category:
            sql += ' AND category = ?'
            params.append(category)
        
        if min_price:
            sql += ' AND price >= ?'
            params.append(min_price)
        
        if max_price:
            sql += ' AND price <= ?'
            params.append(max_price)
        
        sql += ' ORDER BY rating DESC, name ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        products = cursor.fetchall()
        conn.close()
        
        return [self._format_product(product) for product in products]
    
    def get_product_by_id(self, product_id):
        """Get single product by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, price, description, stock_quantity,
                   brand, rating, image_url, specifications
            FROM products WHERE id = ?
        ''', (product_id,))
        
        product = cursor.fetchone()
        conn.close()
        
        return self._format_product(product) if product else None
    
    def get_categories(self):
        """Get all product categories"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM products ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return categories
    
    def _format_product(self, product):
        """Format product data"""
        return {
            'id': product[0],
            'name': product[1],
            'category': product[2],
            'price': product[3],
            'description': product[4],
            'stock_quantity': product[5],
            'brand': product[6],
            'rating': product[7],
            'image_url': product[8],
            'specifications': product[9]
        }

class ChatSession:
    def __init__(self, db):
        self.db = db
    
    def create_session(self, user_id, session_id):
        """Create new chat session"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_sessions (user_id, session_id)
            VALUES (?, ?)
        ''', (user_id, session_id))
        
        conn.commit()
        conn.close()
    
    def save_message(self, session_id, message_type, content):
        """Save chat message"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_messages (session_id, message_type, content)
            VALUES (?, ?, ?)
        ''', (session_id, message_type, content))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id):
        """Get chat history for session"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_type, content, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return [
            {
                'type': msg[0],
                'content': msg[1],
                'timestamp': msg[2]
            }
            for msg in messages
        ]
