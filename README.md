# E-commerce Chatbot Project

A full-stack e-commerce chatbot application built with Flask backend, Groq AI integration, and a modern JavaScript frontend. The chatbot helps customers discover products, get recommendations, and navigate through an online store.

## 🚀 Features

### 🤖 AI-Powered Chatbot
- **Groq LLM Integration**: Uses DeepSeek R1 model for intelligent conversations
- **Product Recommendations**: Context-aware product suggestions
- **Natural Language Processing**: Understands customer queries and intents
- **Chat History**: Persistent conversation history per session

### 🛍️ E-commerce Functionality
- **Product Search**: Advanced filtering by category, price range, and keywords
- **Product Categories**: Electronics, Books, Clothing, Home & Garden, Sports & Outdoors
- **Product Details**: Comprehensive product information with specifications
- **User Authentication**: Secure login/registration system with JWT tokens

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Glass Morphism**: Modern glassmorphism design aesthetics
- **Real-time Chat**: Smooth chat interface with typing indicators
- **Product Cards**: Interactive product display with hover effects

## 🏗️ Architecture

```
ecommerce-chatbot/
├── backend/
│   ├── app.py              # Flask application and API routes
│   ├── models.py           # Database models and operations
│   ├── chatbot_service.py  # AI chatbot service with Groq integration
│   ├── database.py         # Database initialization and sample data
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
└── frontend/
    ├── index.html         # Main chat interface
    ├── login.html         # Authentication page
    ├── script.js          # Frontend JavaScript logic
    └── styles.css         # Custom CSS styles
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (for live server, optional)
- Groq API Key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-chatbot/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file with:
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

5. **Initialize database**
   ```bash
   python database.py
   ```

6. **Start the backend server**
   ```bash
   python app.py
   ```
   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Serve the frontend**
   
   **Option 1: Using Live Server (VS Code)**
   - Install Live Server extension
   - Right-click on `login.html` → "Open with Live Server"
   
   **Option 2: Using Python**
   ```bash
   python -m http.server 5500
   ```
   
   **Option 3: Using Node.js**
   ```bash
   npx serve .
   ```

3. **Access the application**
   - Open `http://localhost:5500/login.html`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key for AI functionality | Yes |
| `SECRET_KEY` | JWT token secret key | Yes |

### Getting Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for an account
3. Generate an API key
4. Add it to your `.env` file

## 👥 Default Users

The application comes with pre-configured test users:

| Username | Password | Email |
|----------|----------|-------|
| admin | admin123 | admin@example.com |
| user1 | password1 | user1@example.com |
| user2 | password2 | user2@example.com |
| testuser | test123 | test@example.com |

## 📱 Usage

### Authentication
1. Start at the login page (`/login.html`)
2. Use any of the default users or register a new account
3. Successfully authenticated users are redirected to the chat interface

### Chatbot Interaction
1. Type natural language queries about products
2. Examples:
   - "Show me laptops under $1000"
   - "I need wireless headphones"
   - "What books do you recommend?"
   - "Find me Nike shoes"

### Product Discovery
- **Chat-based**: Ask the chatbot for recommendations
- **Filter-based**: Use category and price filters
- **Search**: Use the search functionality
- **Browse**: View product categories and recommendations

## 🔌 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Chat
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/reset` - Reset chat session

### Products
- `GET /api/products/search` - Search products
- `GET /api/products/<id>` - Get product details
- `GET /api/categories` - Get product categories
- `GET /api/recommendations` - Get product recommendations

## 🧪 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Products Table
```sql
CREATE TABLE products (
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
);
```

### Chat Sessions & Messages
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
);
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: SHA-256 password encryption
- **CORS Protection**: Configured CORS for frontend-backend communication
- **Session Management**: Secure session handling with expiration

## 🚀 Deployment

### Backend Deployment
- Deploy to Heroku, Railway, or any Python hosting platform
- Set environment variables in production
- Configure production database (PostgreSQL recommended)

### Frontend Deployment
- Deploy to Netlify, Vercel, or any static hosting
- Update API_BASE_URL in script.js to production backend URL

## 🛠️ Development

### Adding New Products
1. Modify `database.py` to add more sample products
2. Run `python database.py` to update the database

### Customizing AI Responses
1. Edit the system prompt in `chatbot_service.py`
2. Adjust temperature and other Groq parameters
3. Modify product context formatting

### Styling Changes
1. Update `styles.css` for custom styles
2. Modify Tailwind classes in HTML files
3. Adjust glassmorphism effects and animations

## 📦 Dependencies

### Backend
- Flask 2.3.3 - Web framework
- Flask-CORS 4.0.0 - Cross-origin resource sharing
- groq - Groq AI API client
- python-dotenv 1.0.0 - Environment variable management
- PyJWT - JSON Web Token implementation

### Frontend
- Tailwind CSS - Utility-first CSS framework
- Font Awesome - Icon library
- Showdown.js - Markdown to HTML converter

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
- Check if port 5000 is available
- Verify environment variables are set
- Ensure virtual environment is activated

**Frontend can't connect to backend:**
- Verify CORS settings in app.py
- Check API_BASE_URL in script.js
- Ensure backend is running on correct port

**Authentication issues:**
- Clear browser localStorage
- Check JWT token expiration
- Verify SECRET_KEY consistency

**Groq API errors:**
- Verify API key is valid
- Check API quota limits
- Review error messages in console

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the console logs for error details

---

**Built with ❤️ using Flask, Groq AI, and modern web technologies**
