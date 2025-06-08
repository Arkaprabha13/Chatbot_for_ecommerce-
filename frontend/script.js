// --- Configuration ---
const API_BASE_URL = 'http://localhost:5000';

// --- Utility Functions ---
function getToken() {
    return localStorage.getItem('authToken');
}
function getUser() {
    try {
        return JSON.parse(localStorage.getItem('user'));
    } catch {
        return null;
    }
}
function showAlert(message, type = 'error', containerId = 'alert-container') {
    const alertContainer = document.getElementById(containerId);
    const alertMessage = document.getElementById('alert-message');
    if (alertContainer && alertMessage) {
        alertMessage.textContent = message;
        alertMessage.className = `p-4 rounded-md ${type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`;
        alertContainer.classList.remove('hidden');
    }
}
function hideAlert(containerId = 'alert-container') {
    const alertContainer = document.getElementById(containerId);
    if (alertContainer) alertContainer.classList.add('hidden');
}
function toggleLoading(isLoading) {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) indicator.classList.toggle('hidden', !isLoading);
}
async function apiFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
        let errMsg = 'Unknown error';
        try {
            const data = await response.json();
            errMsg = data.message || errMsg;
        } catch {}
        throw new Error(errMsg);
    }
    return response.json();
}
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionId');
    window.location.href = 'login.html';
}

// --- Login/Register Page Logic ---
function initializeLoginPage() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const showRegisterBtn = document.getElementById('show-register');
    const showLoginBtn = document.getElementById('show-login');
    const authContainer = document.getElementById('auth-container');
    const registerContainer = document.getElementById('register-container');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideAlert();
            const username = e.target.username.value;
            const password = e.target.password.value;
            try {
                const data = await apiFetch(`${API_BASE_URL}/api/login`, {
                    method: 'POST',
                    body: JSON.stringify({ username, password }),
                });
                if (data.success) {
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    localStorage.setItem('sessionId', data.session_id);
                    window.location.href = 'index.html';
                } else {
                    showAlert(data.message || 'Login failed.');
                }
            } catch (error) {
                showAlert(error.message);
            }
        });
    }
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideAlert();
            const username = e.target.username.value;
            const email = e.target.email.value;
            const password = e.target.password.value;
            try {
                const data = await apiFetch(`${API_BASE_URL}/api/register`, {
                    method: 'POST',
                    body: JSON.stringify({ username, email, password }),
                });
                if (data.success) {
                    showAlert('Registration successful! Please sign in.', 'success');
                    registerContainer.classList.add('hidden');
                    authContainer.classList.remove('hidden');
                } else {
                    showAlert(data.message || 'Registration failed.');
                }
            } catch (error) {
                showAlert(error.message);
            }
        });
    }
    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', () => {
            authContainer.classList.add('hidden');
            registerContainer.classList.remove('hidden');
            hideAlert();
        });
    }
    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', () => {
            registerContainer.classList.add('hidden');
            authContainer.classList.remove('hidden');
            hideAlert();
        });
    }
}

// --- Main Chat Application Logic ---
function initializeApp() {
    // Redirect if not authenticated
    if (!getToken()) {
        window.location.href = 'login.html';
        return;
    }
    // DOM Elements
    const userWelcome = document.getElementById('user-welcome');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const resetChatBtn = document.getElementById('reset-chat-btn');
    const categoryFilter = document.getElementById('category-filter');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const recommendedProductsContainer = document.getElementById('recommended-products');
    const productResultsContainer = document.getElementById('product-results');
    const productResultsSection = document.getElementById('product-results-section');
    const modal = document.getElementById('product-modal');
    const closeModalBtn = document.getElementById('close-modal');

    // Welcome user
    const user = getUser();
    if (user && userWelcome) {
        userWelcome.textContent = `Welcome, ${user.username}!`;
    }

    function displayMessage(content, sender, timestamp = 'Just now') {
    if (!chatMessages) return;

    // Clean up the content:
    // 1. Remove outer quotes if present
    if (typeof content === 'string' && content.startsWith('"') && content.endsWith('"')) {
        content = content.slice(1, -1);
    }
    // 2. Remove any <think>...</think> blocks
    content = content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();

    // 3. Convert Markdown to HTML using Showdown
    if (window.showdown) {
        const converter = new showdown.Converter();
        content = converter.makeHtml(content);
    } else {
        // fallback: just convert line breaks
        content = content.replace(/\n/g, '<br>');
    }

    const div = document.createElement('div');
    const isUser = sender === 'user';
    div.className = `flex items-start ${isUser ? 'justify-end' : ''}`;
    div.innerHTML = `
        ${!isUser ? `<div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mr-3 flex-shrink-0"><i class="fas fa-robot text-white text-sm"></i></div>` : ''}
        <div class="${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100'} rounded-lg p-3 max-w-xs lg:max-w-md">
            <div class="text-sm">${content}</div>
            <span class="text-xs ${isUser ? 'text-blue-200' : 'text-gray-500'} mt-1 block">${timestamp}</span>
        </div>
        ${isUser ? `<div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center ml-3 flex-shrink-0"><i class="fas fa-user text-gray-700 text-sm"></i></div>` : ''}
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

    // Helper: Render product card
    function renderProductCard(product) {
        return `
        <div class="bg-white border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
            <img src="${product.image_url || 'https://via.placeholder.com/300'}" alt="${product.name}" class="w-full h-40 object-cover">
            <div class="p-4">
                <h4 class="font-semibold text-gray-800 truncate">${product.name}</h4>
                <p class="text-sm text-gray-500">${product.brand}</p>
                <div class="flex justify-between items-center mt-2">
                    <p class="text-lg font-bold text-blue-600">$${Number(product.price).toFixed(2)}</p>
                    <span class="text-sm text-yellow-500"><i class="fas fa-star"></i> ${product.rating}</span>
                </div>
                <button data-product-id="${product.id}" class="view-details-btn w-full mt-4 bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition duration-200">
                    View Details
                </button>
            </div>
        </div>
        `;
    }
    function displayProducts(products, container) {
        if (!container) return;
        if (!products || products.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500 col-span-full">No products found.</p>';
            if (container === productResultsContainer && productResultsSection) {
                productResultsSection.classList.add('hidden');
            }
            return;
        }
        container.innerHTML = products.map(renderProductCard).join('');
        if (container === productResultsContainer && productResultsSection) {
            productResultsSection.classList.remove('hidden');
        }
    }

    // Chat Send
    async function sendMessage(message) {
        if (!message.trim()) return;
        displayMessage(message, 'user');
        if (chatInput) chatInput.value = '';
        toggleLoading(true);
        try {
            const data = await apiFetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                body: JSON.stringify({ message }),
            });
            if (data.success) {
                displayMessage(data.response, 'bot');
                if (data.products && data.products.length > 0) {
                    displayProducts(data.products, productResultsContainer);
                }
            } else {
                displayMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            displayMessage(`Error: ${error.message}`, 'bot');
        } finally {
            toggleLoading(false);
        }
    }

    // Fetch and display categories
    async function fetchAndDisplayCategories() {
        if (!categoryFilter) return;
        try {
            const data = await apiFetch(`${API_BASE_URL}/api/categories`);
            if (data.success) {
                data.categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categoryFilter.appendChild(option);
                });
            }
        } catch {}
    }

    // Fetch and display recommendations
    async function fetchAndDisplayRecommendations() {
        if (!recommendedProductsContainer) return;
        try {
            const data = await apiFetch(`${API_BASE_URL}/api/recommendations?limit=4`);
            if (data.success) {
                recommendedProductsContainer.innerHTML = data.products.map(p => `
                    <div class="flex items-center space-x-3">
                        <img src="${p.image_url || 'https://via.placeholder.com/50'}" alt="${p.name}" class="w-12 h-12 rounded-md object-cover">
                        <div>
                            <p class="text-sm font-medium text-gray-800">${p.name}</p>
                            <p class="text-sm text-blue-600 font-semibold">$${Number(p.price).toFixed(2)}</p>
                        </div>
                    </div>
                `).join('');
            }
        } catch {}
    }

    // Fetch and display chat history
    async function fetchChatHistory() {
        if (!chatMessages) return;
        try {
            const data = await apiFetch(`${API_BASE_URL}/api/chat/history`);
            if (data.success && data.history.length > 0) {
                data.history.forEach(msg => {
                    const localTime = new Date(msg.timestamp + 'Z').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    displayMessage(msg.content, msg.type, localTime);
                });
            }
        } catch {}
    }

    // Show product modal
    async function showProductModal(productId) {
        if (!modal) return;
        try {
            toggleLoading(true);
            const data = await apiFetch(`${API_BASE_URL}/api/products/${productId}`);
            if (data.success) {
                const product = data.product;
                document.getElementById('modal-product-name').textContent = product.name;
                let specsHtml = '';
                try {
                    const specs = JSON.parse(product.specifications);
                    specsHtml = Object.entries(specs).map(([key, value]) => `
                        <div class="flex justify-between py-2 border-b">
                            <span class="font-medium text-gray-600 capitalize">${key.replace(/_/g, ' ')}</span>
                            <span class="text-gray-800">${value}</span>
                        </div>
                    `).join('');
                } catch {}
                document.getElementById('modal-content').innerHTML = `
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <img src="${product.image_url || 'https://via.placeholder.com/400'}" alt="${product.name}" class="w-full rounded-lg shadow-md">
                        </div>
                        <div>
                            <p class="text-gray-600 mb-4">${product.description}</p>
                            <div class="text-3xl font-bold text-blue-600 mb-4">$${Number(product.price).toFixed(2)}</div>
                            <div class="flex items-center space-x-4 mb-4">
                                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">In Stock: ${product.stock_quantity}</span>
                                <span class="text-yellow-500"><i class="fas fa-star"></i> ${product.rating}</span>
                            </div>
                            <h3 class="font-bold text-lg mb-2">Specifications</h3>
                            <div class="space-y-1 text-sm">${specsHtml}</div>
                        </div>
                    </div>
                `;
                modal.classList.remove('hidden');
            }
        } catch {} finally {
            toggleLoading(false);
        }
    }

    // Handle product filter search
    async function handleFilterSearch() {
        if (!productResultsContainer) return;
        const category = categoryFilter ? categoryFilter.value : '';
        const minPrice = document.getElementById('min-price')?.value;
        const maxPrice = document.getElementById('max-price')?.value;
        let queryParams = new URLSearchParams({ limit: 12 });
        if (category) queryParams.append('category', category);
        if (minPrice) queryParams.append('min_price', minPrice);
        if (maxPrice) queryParams.append('max_price', maxPrice);
        toggleLoading(true);
        try {
            const data = await apiFetch(`${API_BASE_URL}/api/products/search?${queryParams.toString()}`);
            if (data.success) {
                displayProducts(data.products, productResultsContainer);
            }
        } catch {} finally {
            toggleLoading(false);
        }
    }

    // Reset chat session
    async function resetChat() {
        if (!confirm('Are you sure you want to start a new chat session?')) return;
        try {
            toggleLoading(true);
            const data = await apiFetch(`${API_BASE_URL}/api/chat/reset`, { method: 'POST' });
            if (data.success) window.location.reload();
            else alert('Failed to reset chat session.');
        } catch {} finally {
            toggleLoading(false);
        }
    }

    // --- Event Listeners ---
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage(chatInput.value);
        });
    }
    if (sendBtn) {
        sendBtn.addEventListener('click', () => sendMessage(chatInput.value));
    }
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    if (resetChatBtn) {
        resetChatBtn.addEventListener('click', resetChat);
    }
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', handleFilterSearch);
    }
    // Delegate product card clicks for modal
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.view-details-btn');
        if (btn) showProductModal(btn.dataset.productId);
    });
    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });
    }

    // --- Initial Data Load ---
    fetchAndDisplayCategories();
    fetchAndDisplayRecommendations();
    fetchChatHistory();
}

// --- Page Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('login-form')) {
        initializeLoginPage();
    } else if (document.getElementById('chat-form')) {
        initializeApp();
    }
});
