import sqlite3
import json
from models import Database, User, Product, ChatSession
def add_sample_users():
    db = Database()
    user_service = User(db)
    
    # Add 4 sample users
    users_to_add = [
        ('admin', 'admin@example.com', 'admin123'),
        ('user1', 'user1@example.com', 'password1'),
        ('user2', 'user2@example.com', 'password2'),
        ('testuser', 'test@example.com', 'test123')
    ]
    
    print("Adding sample users to database...")
    
    for username, email, password in users_to_add:
        user_id = user_service.create_user(username, email, password)
        if user_id:
            print(f"✓ User '{username}' added successfully with ID {user_id}")
        else:
            print(f"✗ Failed to add user '{username}' (may already exist)")
    
    print("\nSample users added! You can now login with:")
    print("Username: admin, Password: admin123")
    print("Username: user1, Password: password1")
    print("Username: user2, Password: password2")
    print("Username: testuser, Password: test123")
def populate_sample_data():
    """Populate database with 100+ sample products"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Sample electronics products
    electronics_products = [
        {
            'name': 'iPhone 15 Pro',
            'category': 'Electronics',
            'price': 999.99,
            'description': 'Latest iPhone with A17 Pro chip and titanium design',
            'stock_quantity': 50,
            'brand': 'Apple',
            'rating': 4.8,
            'image_url': '/static/products/iphone15pro.jpg',
            'specifications': json.dumps({
                'display': '6.1-inch Super Retina XDR',
                'storage': '128GB',
                'camera': '48MP Main camera',
                'battery': 'Up to 23 hours video playback'
            })
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'category': 'Electronics',
            'price': 1199.99,
            'description': 'Premium Android smartphone with S Pen and AI features',
            'stock_quantity': 30,
            'brand': 'Samsung',
            'rating': 4.7,
            'image_url': '/static/products/galaxy_s24_ultra.jpg',
            'specifications': json.dumps({
                'display': '6.8-inch Dynamic AMOLED 2X',
                'storage': '256GB',
                'camera': '200MP Main camera',
                'battery': '5000mAh'
            })
        },
        {
            'name': 'MacBook Pro 14-inch M3',
            'category': 'Electronics',
            'price': 1599.99,
            'description': 'Professional laptop with M3 chip for creative workflows',
            'stock_quantity': 25,
            'brand': 'Apple',
            'rating': 4.9,
            'image_url': '/static/products/macbook_pro_14.jpg',
            'specifications': json.dumps({
                'processor': 'Apple M3 chip',
                'memory': '8GB unified memory',
                'storage': '512GB SSD',
                'display': '14.2-inch Liquid Retina XDR'
            })
        },
        {
            'name': 'Dell XPS 13',
            'category': 'Electronics',
            'price': 899.99,
            'description': 'Ultra-portable laptop with InfinityEdge display',
            'stock_quantity': 40,
            'brand': 'Dell',
            'rating': 4.5,
            'image_url': '/static/products/dell_xps_13.jpg',
            'specifications': json.dumps({
                'processor': 'Intel Core i7-1355U',
                'memory': '16GB LPDDR5',
                'storage': '512GB SSD',
                'display': '13.4-inch FHD+'
            })
        },
        {
            'name': 'Sony WH-1000XM5',
            'category': 'Electronics',
            'price': 399.99,
            'description': 'Industry-leading noise canceling wireless headphones',
            'stock_quantity': 60,
            'brand': 'Sony',
            'rating': 4.6,
            'image_url': '/static/products/sony_wh1000xm5.jpg',
            'specifications': json.dumps({
                'battery_life': '30 hours',
                'noise_canceling': 'Industry-leading',
                'connectivity': 'Bluetooth 5.2',
                'weight': '250g'
            })
        }
    ]
    
    # Add more product categories
    books_products = [
        {
            'name': 'The Psychology of Money',
            'category': 'Books',
            'price': 14.99,
            'description': 'Timeless lessons on wealth, greed, and happiness',
            'stock_quantity': 100,
            'brand': 'Harriman House',
            'rating': 4.7,
            'image_url': '/static/products/psychology_of_money.jpg',
            'specifications': json.dumps({
                'author': 'Morgan Housel',
                'pages': 256,
                'format': 'Paperback',
                'language': 'English'
            })
        },
        {
            'name': 'Atomic Habits',
            'category': 'Books',
            'price': 13.99,
            'description': 'An Easy & Proven Way to Build Good Habits & Break Bad Ones',
            'stock_quantity': 80,
            'brand': 'Avery',
            'rating': 4.8,
            'image_url': '/static/products/atomic_habits.jpg',
            'specifications': json.dumps({
                'author': 'James Clear',
                'pages': 320,
                'format': 'Hardcover',
                'language': 'English'
            })
        }
    ]
    
    # Generate more products programmatically
    all_products = electronics_products + books_products
    
    # Add clothing items
    clothing_items = []
    clothing_brands = ['Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo']
    clothing_types = ['T-Shirt', 'Jeans', 'Hoodie', 'Sneakers', 'Jacket']
    
    for i in range(20):
        brand = clothing_brands[i % len(clothing_brands)]
        item_type = clothing_types[i % len(clothing_types)]
        clothing_items.append({
            'name': f'{brand} {item_type} - Style {i+1}',
            'category': 'Clothing',
            'price': round(29.99 + (i * 5.5), 2),
            'description': f'Premium {item_type.lower()} from {brand} with modern design',
            'stock_quantity': 50 + i,
            'brand': brand,
            'rating': round(4.0 + (i % 10) * 0.1, 1),
            'image_url': f'/static/products/{brand.lower()}_{item_type.lower()}_{i+1}.jpg',
            'specifications': json.dumps({
                'material': 'Cotton blend',
                'sizes': 'XS, S, M, L, XL',
                'care': 'Machine washable',
                'origin': 'Made in Vietnam'
            })
        })
    
    all_products.extend(clothing_items)
    
    # Add home & garden items
    home_items = []
    home_categories = ['Furniture', 'Kitchen', 'Decor', 'Garden', 'Storage']
    
    for i in range(30):
        category = home_categories[i % len(home_categories)]
        home_items.append({
            'name': f'{category} Item {i+1}',
            'category': 'Home & Garden',
            'price': round(49.99 + (i * 12.3), 2),
            'description': f'High-quality {category.lower()} item for your home',
            'stock_quantity': 25 + i,
            'brand': f'Brand{i % 5 + 1}',
            'rating': round(3.8 + (i % 12) * 0.1, 1),
            'image_url': f'/static/products/home_{category.lower()}_{i+1}.jpg',
            'specifications': json.dumps({
                'dimensions': f'{20+i}x{15+i}x{10+i} cm',
                'weight': f'{1+i*0.5} kg',
                'material': 'Premium materials',
                'warranty': '2 years'
            })
        })
    
    all_products.extend(home_items)
    
    # Add sports & outdoors items
    sports_items = []
    sports_brands = ['Nike', 'Adidas', 'Under Armour', 'Puma', 'Reebok']
    
    for i in range(25):
        brand = sports_brands[i % len(sports_brands)]
        sports_items.append({
            'name': f'{brand} Sports Equipment {i+1}',
            'category': 'Sports & Outdoors',
            'price': round(79.99 + (i * 8.7), 2),
            'description': f'Professional sports equipment from {brand}',
            'stock_quantity': 35 + i,
            'brand': brand,
            'rating': round(4.2 + (i % 8) * 0.1, 1),
            'image_url': f'/static/products/sports_{brand.lower()}_{i+1}.jpg',
            'specifications': json.dumps({
                'type': 'Professional grade',
                'suitable_for': 'All skill levels',
                'warranty': '1 year',
                'certification': 'Official standards'
            })
        })
    
    all_products.extend(sports_items)
    
    # Insert all products
    for product in all_products:
        cursor.execute('''
            INSERT INTO products (name, category, price, description, stock_quantity,
                                brand, rating, image_url, specifications)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['name'],
            product['category'],
            product['price'],
            product['description'],
            product['stock_quantity'],
            product['brand'],
            product['rating'],
            product['image_url'],
            product['specifications']
        ))
    
    conn.commit()
    conn.close()
    print(f"Successfully populated database with {len(all_products)} products")

if __name__ == "__main__":
    populate_sample_data()    
    add_sample_users()

