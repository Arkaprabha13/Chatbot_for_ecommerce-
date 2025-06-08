from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import jwt  # Make sure PyJWT is installed: pip install PyJWT
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
from models import Database, User, Product, ChatSession
from chatbot_service import ChatbotService

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')

# CORS Configuration
CORS(app, 
     supports_credentials=True,
     origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:3000", "http://localhost:3000"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Initialize database and services
db = Database()
user_service = User(db)
product_service = Product(db)
chat_service = ChatSession(db)
chatbot_service = ChatbotService(db)

def generate_token(user_id, session_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'session_id': session_id,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

@app.before_request
def before_request():
    """Debug request information"""
    print(f"\n=== REQUEST DEBUG ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Origin: {request.headers.get('Origin', 'None')}")
    print(f"Authorization: {request.headers.get('Authorization', 'None')}")

@app.after_request
def after_request(response):
    """Add CORS headers"""
    origin = request.headers.get('Origin')
    if origin in ['http://127.0.0.1:5500', 'http://localhost:5500', 'http://127.0.0.1:3000', 'http://localhost:3000']:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    
    print(f"=== RESPONSE DEBUG ===")
    print(f"Status: {response.status_code}")
    print("=====================\n")
    
    return response

@app.route('/')
def home():
    return jsonify({"message": "E-commerce Chatbot API is running!"})

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    """User registration endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    print(f"Registration data: {data}")
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    user_id = user_service.create_user(
        data['username'], 
        data['email'], 
        data['password']
    )
    
    if user_id:
        print(f"User registered successfully with ID: {user_id}")
        return jsonify({
            'success': True, 
            'message': 'User registered successfully',
            'user_id': user_id
        })
    else:
        print("Registration failed - user already exists")
        return jsonify({
            'success': False, 
            'message': 'Username or email already exists'
        }), 400

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """User login endpoint with token generation"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    print(f"Login attempt with data: {data}")
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
    user = user_service.authenticate_user(data['username'], data['password'])
    print(f"Authentication result: {user}")
    
    if user:
        # Generate session ID and token
        session_id = str(uuid.uuid4())
        token = generate_token(user['id'], session_id)
        
        print(f"Generated token for user: {user['username']}, session: {session_id}")
        
        # Create chat session
        try:
            chat_service.create_session(user['id'], session_id)
            print(f"Chat session created: {session_id}")
        except Exception as e:
            print(f"Error creating chat session: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user,
            'token': token,
            'session_id': session_id
        })
    else:
        print("Authentication failed")
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

@app.route('/api/logout', methods=['POST', 'OPTIONS'])
def logout():
    """User logout endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
        
    print(f"Logout request")
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Chat endpoint for processing user messages"""
    # Handle OPTIONS request FIRST, before token validation
    if request.method == 'OPTIONS':
        print("✅ OPTIONS request for /api/chat - returning 200")
        return '', 200
    
    # Apply token validation only for non-OPTIONS requests
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        print("❌ No token provided")
        return jsonify({'success': False, 'message': 'Token is missing!'}), 401
    
    try:
        # Decode the token
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = data['user_id']
        session_id = data['session_id']
        
        print(f"✅ Token authenticated for user_id: {user_id}")
        
        # Verify user exists
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid token!'}), 401
        
        # Process chat message
        request_data = request.get_json()
        if not request_data or 'message' not in request_data:
            return jsonify({'success': False, 'message': 'Message is required'}), 400
        
        user_message = request_data['message']
        print(f"✅ Processing message: '{user_message}'")
        
        # Save user message
        chat_service.save_message(session_id, 'user', user_message)
        
        # Get chat history
        chat_history = chat_service.get_chat_history(session_id)
        
        # Process with chatbot service
        result = chatbot_service.process_user_message(user_message, chat_history)
        
        if result['success']:
            chat_service.save_message(session_id, 'bot', result['response'])
            return jsonify({
                'success': True,
                'response': result['response'],
                'products': result['products']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error processing message',
                'error': result.get('error', 'Unknown error')
            }), 500
            
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Token is invalid!'}), 401
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/products/search', methods=['GET', 'OPTIONS'])
def search_products():
    """Search products endpoint (public)"""
    if request.method == 'OPTIONS':
        return '', 200
        
    query = request.args.get('q', '')
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    limit = request.args.get('limit', 20, type=int)
    
    try:
        products = product_service.search_products(
            query, category, min_price, max_price, limit
        )
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        print(f"Product search error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error searching products',
            'error': str(e)
        }), 500

@app.route('/api/products/<int:product_id>', methods=['GET', 'OPTIONS'])
def get_product(product_id):
    """Get single product by ID (public)"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        product = product_service.get_product_by_id(product_id)
        
        if product:
            return jsonify({'success': True, 'product': product})
        else:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
    except Exception as e:
        print(f"Get product error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving product',
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET', 'OPTIONS'])
def get_categories():
    """Get all product categories (public)"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        categories = product_service.get_categories()
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        print(f"Get categories error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving categories',
            'error': str(e)
        }), 500

@app.route('/api/chat/history', methods=['GET', 'OPTIONS'])
def get_chat_history():
    """Get chat history for current session"""
    if request.method == 'OPTIONS':
        return '', 200
        
    # Token validation for protected endpoint
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return jsonify({'success': False, 'message': 'Token is missing!'}), 401
    
    try:
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        session_id = data['session_id']
        history = chat_service.get_chat_history(session_id)
        
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        print(f"Get chat history error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving chat history',
            'error': str(e)
        }), 500

@app.route('/api/chat/reset', methods=['POST', 'OPTIONS'])
def reset_chat():
    """Reset chat session"""
    if request.method == 'OPTIONS':
        return '', 200
        
    # Token validation for protected endpoint
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return jsonify({'success': False, 'message': 'Token is missing!'}), 401
    
    try:
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = data['user_id']
        
        # Create new session
        new_session_id = str(uuid.uuid4())
        chat_service.create_session(user_id, new_session_id)
        
        print(f"Chat session reset to: {new_session_id}")
        
        return jsonify({'success': True, 'message': 'Chat session reset'})
    except Exception as e:
        print(f"Reset chat error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error resetting chat',
            'error': str(e)
        }), 500

@app.route('/api/recommendations', methods=['GET', 'OPTIONS'])
def get_recommendations():
    """Get product recommendations (public)"""
    if request.method == 'OPTIONS':
        return '', 200
        
    category = request.args.get('category')
    limit = request.args.get('limit', 8, type=int)
    
    try:
        products = chatbot_service.get_product_recommendations(category, limit)
        
        return jsonify({
            'success': True,
            'products': products
        })
    except Exception as e:
        print(f"Get recommendations error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error getting recommendations',
            'error': str(e)
        }), 500

def create_sample_users():
    """Create sample users if they don't exist"""
    try:
        admin_user = user_service.authenticate_user('admin', 'admin123')
        if not admin_user:
            users_to_add = [
                ('admin', 'admin@example.com', 'admin123'),
                ('user1', 'user1@example.com', 'password1'),
                ('user2', 'user2@example.com', 'password2'),
                ('testuser', 'test@example.com', 'test123')
            ]
            
            print("Creating sample users...")
            for username, email, password in users_to_add:
                user_id = user_service.create_user(username, email, password)
                if user_id:
                    print(f"✅ Created user: {username}")
                else:
                    print(f"❌ Failed to create user: {username}")
    except Exception as e:
        print(f"Error creating sample users: {e}")

if __name__ == '__main__':
    print("🚀 Starting E-commerce Chatbot API...")
    
    # Populate database if it's empty
    try:
        from database import populate_sample_data
        test_products = product_service.search_products("", limit=1)
        if not test_products:
            print("📦 Populating database with sample data...")
            populate_sample_data()
        else:
            print(f"📦 Database already contains products")
        
        create_sample_users()
            
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎯 API ready at http://localhost:5000")
    print("🔧 Debug mode enabled - check console for detailed logs")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
