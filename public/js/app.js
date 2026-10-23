/**
 * Mr. Boy SpecialTea — Application JavaScript
 *
 * Handles:
 * - Authentication (Register, Login, Logout, Session State)
 * - Section Navigation (Home, Menu, Cart, About, Contact, Admin)
 * - Cart Management & Real-time Total Calculation
 * - Add-ons & Receipt Generation
 * - Admin Order Management (Protected by Admin Role)
 */

/* ============================================================
   GLOBAL STATE
   ============================================================ */

let currentUser = null;
let cart = [];
let total = 0;


/* ============================================================
   INITIALIZATION
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    // Check initial user authentication status
    checkAuthStatus();

    // Fade-in home section on load
    const home = document.getElementById('home');
    if (home) {
        home.style.opacity = 0;
        home.style.display = 'block';
        home.style.transition = 'opacity 1s ease';
        requestAnimationFrame(() => {
            home.style.opacity = 1;
        });
    }

    // "Start Ordering" button → navigate to menu
    const startBtn = document.getElementById('start-ordering');
    if (startBtn) {
        startBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const current = document.querySelector('.section.active');
            if (current) {
                current.style.opacity = 0;
                setTimeout(() => {
                    showSection('menu');
                }, 400);
            } else {
                showSection('menu');
            }
        });
    }

    // Close modal on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAuthModal();
        }
    });
});


/* ============================================================
   AUTHENTICATION (REGISTER / LOGIN / LOGOUT)
   ============================================================ */

/**
 * Check if the user is already logged in (via API or localStorage fallback).
 */
function checkAuthStatus() {
    fetch('api/current_user.php')
        .then(res => res.json())
        .then(data => {
            if (data.logged_in && data.user) {
                currentUser = data.user;
                localStorage.setItem('mr_boy_user', JSON.stringify(currentUser));
            } else {
                // Check localStorage backup
                const cached = localStorage.getItem('mr_boy_user');
                if (cached) {
                    try {
                        currentUser = JSON.parse(cached);
                    } catch(e) {
                        currentUser = null;
                    }
                } else {
                    currentUser = null;
                }
            }
            updateAuthUI();
        })
        .catch(() => {
            const cached = localStorage.getItem('mr_boy_user');
            if (cached) {
                try {
                    currentUser = JSON.parse(cached);
                } catch(e) {
                    currentUser = null;
                }
            }
            updateAuthUI();
        });
}

/**
 * Update Navbar and Admin view based on auth state.
 */
function updateAuthUI() {
    const navAuth = document.getElementById('nav-auth');
    if (navAuth) {
        if (currentUser) {
            const roleBadge = currentUser.role === 'admin' 
                ? '<span class="auth-role-tag">Admin</span>' 
                : '';

            navAuth.innerHTML = `
                <div class="auth-user-badge">
                    <span>👤 ${currentUser.fullname}</span>
                    ${roleBadge}
                </div>
                <button onclick="handleLogout()" class="auth-logout-btn">🚪 Logout</button>
            `;
        } else {
            navAuth.innerHTML = `
                <button onclick="openAuthModal('login')" class="auth-nav-btn">🔑 Login / Register</button>
            `;
        }
    }

    // Auto-fill customer name in cart if logged in
    const nameInput = document.getElementById('customer-name');
    if (nameInput && currentUser && !nameInput.value.trim()) {
        nameInput.value = currentUser.fullname;
    }

    // Update Admin dashboard view gate
    updateAdminGate();
}

/**
 * Update Admin tab contents according to role.
 */
function updateAdminGate() {
    const gate = document.getElementById('admin-auth-gate');
    const content = document.getElementById('admin-content');

    if (!gate || !content) return;

    if (currentUser && currentUser.role === 'admin') {
        gate.style.display = 'none';
        content.style.display = 'block';
        loadOrders();
    } else {
        gate.style.display = 'block';
        content.style.display = 'none';
    }
}

/**
 * Open the Auth Modal on Login or Register tab.
 */
function openAuthModal(tab = 'login') {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.style.display = 'flex';
        clearAuthAlert();
        switchAuthTab(tab);
    }
}

/**
 * Close the Auth Modal.
 */
function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.style.display = 'none';
        clearAuthAlert();
    }
}

/**
 * Switch between Login and Register tabs.
 */
function switchAuthTab(tab) {
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');
    const tabLoginBtn = document.getElementById('tab-login-btn');
    const tabRegBtn = document.getElementById('tab-register-btn');

    clearAuthAlert();

    if (tab === 'login') {
        if (loginForm) loginForm.style.display = 'flex';
        if (regForm) regForm.style.display = 'none';
        if (tabLoginBtn) tabLoginBtn.classList.add('active');
        if (tabRegBtn) tabRegBtn.classList.remove('active');
    } else {
        if (loginForm) loginForm.style.display = 'none';
        if (regForm) regForm.style.display = 'flex';
        if (tabLoginBtn) tabLoginBtn.classList.remove('active');
        if (tabRegBtn) tabRegBtn.classList.add('active');
    }
}

/**
 * Show alert banner in auth modal.
 */
function showAuthAlert(message, type = 'error') {
    const alertBox = document.getElementById('auth-alert');
    if (alertBox) {
        alertBox.textContent = message;
        alertBox.className = `auth-alert ${type}`;
        alertBox.style.display = 'block';
    }
}

function clearAuthAlert() {
    const alertBox = document.getElementById('auth-alert');
    if (alertBox) {
        alertBox.style.display = 'none';
        alertBox.textContent = '';
    }
}

/**
 * Handle Login Form Submission.
 */
function handleLogin(e) {
    e.preventDefault();
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const submitBtn = document.getElementById('login-submit-btn');

    const username = usernameInput ? usernameInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';

    if (!username || !password) {
        showAuthAlert("Please enter both username/email and password.");
        return;
    }

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Logging in...";
    }

    fetch('api/login.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Login ☕";
        }

        if (data.status === 'success') {
            currentUser = data.user;
            localStorage.setItem('mr_boy_user', JSON.stringify(currentUser));
            showAuthAlert(data.message || "Login successful!", 'success');
            setTimeout(() => {
                closeAuthModal();
                updateAuthUI();
                // If on admin tab and user is admin, refresh view
                const adminSec = document.getElementById('admin');
                if (adminSec && adminSec.classList.contains('active')) {
                    updateAdminGate();
                }
            }, 700);
        } else {
            showAuthAlert(data.message || "Invalid login credentials.", 'error');
        }
    })
    .catch(err => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Login ☕";
        }
        showAuthAlert("Could not connect to server. Check your connection.", 'error');
    });
}

/**
 * Handle Registration Form Submission.
 */
function handleRegister(e) {
    e.preventDefault();
    const fullnameInput = document.getElementById('reg-fullname');
    const usernameInput = document.getElementById('reg-username');
    const emailInput = document.getElementById('reg-email');
    const passwordInput = document.getElementById('reg-password');
    const submitBtn = document.getElementById('reg-submit-btn');

    const fullname = fullnameInput ? fullnameInput.value.trim() : '';
    const username = usernameInput ? usernameInput.value.trim() : '';
    const email = emailInput ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';

    if (!fullname || !username || !email || !password) {
        showAuthAlert("Please fill in all fields.");
        return;
    }

    if (password.length < 6) {
        showAuthAlert("Password must be at least 6 characters.");
        return;
    }

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Creating Account...";
    }

    fetch('api/register.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullname, username, email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Create Account ✨";
        }

        if (data.status === 'success') {
            currentUser = data.user;
            localStorage.setItem('mr_boy_user', JSON.stringify(currentUser));
            showAuthAlert(data.message || "Account created successfully!", 'success');
            setTimeout(() => {
                closeAuthModal();
                updateAuthUI();
            }, 800);
        } else {
            showAuthAlert(data.message || "Registration failed.", 'error');
        }
    })
    .catch(err => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Create Account ✨";
        }
        showAuthAlert("Could not connect to server. Check your connection.", 'error');
    });
}

/**
 * Handle Logout.
 */
function handleLogout() {
    fetch('api/logout.php', { method: 'POST' })
        .finally(() => {
            currentUser = null;
            localStorage.removeItem('mr_boy_user');
            updateAuthUI();
            alert("You have been logged out.");
            showSection('home');
        });
}


/* ============================================================
   SECTION NAVIGATION
   ============================================================ */

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        if (section.id === sectionId) {
            section.classList.add('active');
            section.style.display = 'block';
            section.style.opacity = 0;
            section.style.transition = 'opacity 0.4s ease';
            requestAnimationFrame(() => {
                section.style.opacity = 1;
            });

            // Refresh cart UI when switching to cart
            if (sectionId === 'cart') {
                renderCart();
                updatePearlButton();
                updateGenerateButton();
                // Pre-fill name if user logged in
                const nameInput = document.getElementById('customer-name');
                if (nameInput && currentUser && !nameInput.value.trim()) {
                    nameInput.value = currentUser.fullname;
                }
            }

            // Refresh admin view
            if (sectionId === 'admin') {
                updateAdminGate();
            }
        } else {
            section.classList.remove('active');
            section.style.opacity = 0;
            section.style.display = 'none';
        }
    });
}


/* ============================================================
   CART MANAGEMENT
   ============================================================ */

/**
 * Add an item to the cart and switch to cart view.
 */
function addToCart(item, price) {
    cart.push({ item: item, price: price, addons: [] });
    total += price;
    renderCart();
    updatePearlButton();
    updateGenerateButton();
    showSection('cart');
}

/**
 * Add an add-on to the last item in the cart.
 */
function addAddonToLastItem(addonName, addonPrice) {
    if (cart.length === 0) {
        alert("Please order a drink first.");
        return;
    }
    const lastItem = cart[cart.length - 1];
    lastItem.addons.push({ name: addonName, price: addonPrice });
    total += addonPrice;
    renderCart();
}

/**
 * Render the cart items list and total.
 */
function renderCart() {
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    if (!cartItems || !cartTotal) return;

    cartItems.innerHTML = '';
    cart.forEach((cartItem, index) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${cartItem.item}</strong> - ₱${cartItem.price}`;

        // Render add-ons
        if (cartItem.addons.length > 0) {
            const addonList = document.createElement('ul');
            cartItem.addons.forEach(addon => {
                const addonLi = document.createElement('li');
                addonLi.textContent = `+ ${addon.name} (₱${addon.price})`;
                addonList.appendChild(addonLi);
            });
            li.appendChild(addonList);
        }

        // Cancel button per item
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = "❌";
        cancelBtn.style.marginLeft = "10px";
        cancelBtn.onclick = () => removeItem(index);
        li.appendChild(cancelBtn);

        cartItems.appendChild(li);
    });

    cartTotal.textContent = total;
}

/**
 * Remove an item from the cart by index.
 */
function removeItem(index) {
    const item = cart[index];
    if (!item) return;
    total -= item.price;
    item.addons.forEach(addon => total -= addon.price);
    cart.splice(index, 1);
    renderCart();
    updatePearlButton();
    updateGenerateButton();
}

/**
 * Clear the entire cart.
 */
function clearCart() {
    cart = [];
    total = 0;
    renderCart();
    updatePearlButton();
    updateGenerateButton();
    const receipt = document.getElementById('receipt');
    if (receipt) receipt.style.display = 'none';
}

/**
 * Enable/disable the Pearl add-on button based on cart state.
 */
function updatePearlButton() {
    const pearlBtn = document.getElementById('pearl-btn');
    if (pearlBtn) {
        pearlBtn.disabled = (cart.length === 0);
    }
}

/**
 * Enable/disable the Generate Receipt button based on cart state.
 */
function updateGenerateButton() {
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.disabled = (cart.length === 0);
    }
}


/* ============================================================
   RECEIPT GENERATION & ORDER SUBMISSION
   ============================================================ */

function generateReceipt() {
    if (cart.length === 0) {
        alert("Your cart is empty.");
        return;
    }

    if (!currentUser) {
        alert("Please log in or register before submitting your order.");
        openAuthModal('login');
        return;
    }

    const nameInput = document.getElementById('customer-name');
    const name = nameInput ? nameInput.value.trim() : (currentUser ? currentUser.fullname : "");

    if (!name) {
        alert("Please enter your name before generating receipt.");
        if (nameInput) nameInput.focus();
        return;
    }

    fetch('api/submit_order.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: currentUser ? currentUser.id : null,
            customer_name: name,
            order_details: cart.map(item => item.item).join(", "),
            total_price: total
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert("Success! Order saved to database.");

            // Populate receipt
            const receiptItems = document.getElementById('receipt-items');
            if (receiptItems) {
                receiptItems.innerHTML = '';
                cart.forEach(cartItem => {
                    const li = document.createElement('li');
                    li.textContent = `${cartItem.item} - ₱${cartItem.price}`;
                    receiptItems.appendChild(li);
                });
            }

            const rName  = document.getElementById('receipt-name');
            const rTotal = document.getElementById('receipt-total');
            const rDiv   = document.getElementById('receipt');

            if (rName)  rName.textContent  = name;
            if (rTotal) rTotal.textContent = total;
            if (rDiv)   rDiv.style.display = 'block';
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Failed to connect to server. Check Console (F12).");
    });
}


/* ============================================================
   ADMIN — ORDER MANAGEMENT
   ============================================================ */

/**
 * Load all orders into the admin dashboard table.
 */
function loadOrders() {
    const tableBody = document.getElementById('admin-order-list');
    if (!tableBody) return;

    fetch('api/fetch_orders.php')
        .then(response => response.json())
        .then(data => {
            tableBody.innerHTML = "";

            if (!data || data.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="5" style="padding: 20px; text-align: center; color: #888;">No orders found.</td>
                    </tr>
                `;
                return;
            }

            data.forEach(order => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="padding:8px; border:1px solid #ddd;">${order.order_date}</td>
                    <td style="padding:8px; border:1px solid #ddd;">${order.customer_name}</td>
                    <td style="padding:8px; border:1px solid #ddd;">${order.order_details}</td>
                    <td style="padding:8px; border:1px solid #ddd;">₱${order.total_price}</td>
                    <td style="padding:8px; border:1px solid #ddd;">
                        <button onclick="deleteOrder(${order.id})">Done</button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error fetching orders:', error));
}

/**
 * Delete a single order and refresh the table.
 */
function deleteOrder(id) {
    fetch('api/delete_order.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            loadOrders();
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(err => console.error('Delete error:', err));
}

/**
 * Clear all order records.
 */
function clearAllOrders() {
    if (!confirm("Are you sure you want to clear ALL order records?")) return;

    fetch('api/clear_orders.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert("All records cleared.");
            loadOrders();
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(err => console.error('Clear error:', err));
}


/* ============================================================
   FEATURED PRODUCTS CAROUSEL SLIDER (HOME PAGE)
   ============================================================ */

let currentSlideIndex = 0;
const totalSlides = 6;
let sliderTimer = null;
let isSliderPaused = false;

function initFeaturedSlider() {
    startSliderAutoPlay();
}

function startSliderAutoPlay() {
    if (sliderTimer) clearInterval(sliderTimer);
    sliderTimer = setInterval(() => {
        if (!isSliderPaused) {
            nextSlide();
        }
    }, 4500);
}

function updateSliderView() {
    const track = document.getElementById('carousel-track');
    const pills = document.querySelectorAll('.slider-category-tabs .cat-pill');
    const dots = document.querySelectorAll('.carousel-dots .dot');

    if (track) {
        track.style.transform = `translateX(-${currentSlideIndex * 100}%)`;
    }

    // Update Category Pills
    pills.forEach((pill, idx) => {
        if (idx === currentSlideIndex) {
            pill.classList.add('active');
        } else {
            pill.classList.remove('active');
        }
    });

    // Update Dots
    dots.forEach((dot, idx) => {
        if (idx === currentSlideIndex) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

function jumpToSlide(index) {
    currentSlideIndex = (index + totalSlides) % totalSlides;
    updateSliderView();
}

function prevSlide() {
    currentSlideIndex = (currentSlideIndex - 1 + totalSlides) % totalSlides;
    updateSliderView();
}

function nextSlide() {
    currentSlideIndex = (currentSlideIndex + 1) % totalSlides;
    updateSliderView();
}

function pauseSlider() {
    isSliderPaused = true;
}

function resumeSlider() {
    isSliderPaused = false;
}

// Start slider when document loads
document.addEventListener('DOMContentLoaded', () => {
    initFeaturedSlider();
});

