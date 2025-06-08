import os
from groq import Groq
import json
from models import Product
import re
class ChatbotService:
    def __init__(self, db):
        self.db = db
        self.product_service = Product(db)
        # Initialize Groq client
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
    def process_user_message(self, user_message, chat_history=None):
        """Process user message and return chatbot response with product recommendations"""
        try:
            # Get product context for the AI
            products_context = self._get_products_context(user_message)
            
            # Prepare system prompt
            system_prompt = f"""
            You are a helpful e-commerce sales assistant. Your role is to help customers find products, answer questions about products, and guide them through their shopping experience.
            
            Available product categories: Electronics, Books, Clothing, Home & Garden, Sports & Outdoors
            
            Current product context based on user query:
            {products_context}
            
            Instructions:
            1. Be friendly, helpful, and professional
            2. When recommending products, mention specific product names, prices, and key features
            3. Ask clarifying questions to better understand customer needs
            4. Provide product comparisons when relevant
            5. Guide users through the shopping process
            6. If asked about products not in our inventory, politely explain we don't carry them but suggest alternatives
            7. Keep responses concise but informative
            8. Always try to be helpful and sales-oriented while being genuine
            """
            
            # Prepare messages for Groq API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history if available
            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    if msg['type'] == 'user':
                        messages.append({"role": "user", "content": msg['content']})
                    elif msg['type'] == 'bot':
                        messages.append({"role": "assistant", "content": msg['content']})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from Groq
            completion = self.client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=messages,
                temperature=0.6,
                max_completion_tokens=4096,
                top_p=0.95,
                stream=False,
                stop=None,
            )
            
            bot_response = completion.choices[0].message.content
            bot_response = re.sub(r"<think>.*?</think>", "", bot_response, flags=re.DOTALL).strip()
            if "Answer:" in bot_response:           
                
                bot_response = bot_response.split("Answer:")[-1].strip()
            # Get relevant products for the response
            relevant_products = self._extract_relevant_products(user_message)
            
            return {
                'response': bot_response,
                'products': relevant_products,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team.",
                'products': [],
                'success': False,
                'error': str(e)
            }
    
    def _get_products_context(self, user_message):
        """Get relevant products context for the AI"""
        # Search for products based on user message
        products = self.product_service.search_products(user_message, limit=5)
        
        if not products:
            return "No specific products found for this query."
        
        context = "Relevant products in our inventory:\n"
        for product in products:
            context += f"- {product['name']} by {product['brand']}: ${product['price']} (Rating: {product['rating']}/5)\n"
            context += f"  Description: {product['description']}\n"
            context += f"  Stock: {product['stock_quantity']} available\n\n"
        
        return context
    
    def _extract_relevant_products(self, user_message):
        """Extract and return relevant products for display"""
        return self.product_service.search_products(user_message, limit=6)
    
    def get_product_recommendations(self, category=None, limit=8):
        """Get product recommendations"""
        if category:
            return self.product_service.search_products("", category=category, limit=limit)
        else:
            # Get top-rated products from different categories
            return self.product_service.search_products("", limit=limit)
