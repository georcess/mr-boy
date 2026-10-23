# Mr. Boy SpecialTea - Online Ordering System

A full-stack ordering and store management web application built for Mr. Boy SpecialTea. The platform allows customers to browse the menu, customize drinks, submit orders, and view receipts, while giving store managers tools to handle orders, monitor stock availability, and review inquiries in an admin dashboard.

---

## Overview

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Radix UI primitives, Lucide icons.
- **Backend (Python)**: Flask with SQLite or Turso Cloud Database (`server.py`), session-based authentication, REST API.
- **Backend (PHP / Optional)**: PHP MVC with MySQL support for XAMPP / Apache environments.

---

## Features

### Customer Ordering
- Interactive menu with real-time search and category filtering (Milktea, Iced Coffee, Fruit Tea, Frappe, Hot Cups, Snacks).
- Drink customizations (size selection, sweetness level, add-on pearls).
- Shopping cart with live price calculations, inline item modifications, and floating quick-checkout bar.
- On-screen itemized receipt generation with print support.
- User authentication (registration, login, profile updates, and order history tracking).
- Light / Dark theme toggle with persistent user preference.

### Admin Dashboard
- Role-protected administrative interface.
- Live order queue with status updates (`pending`, `received`, `completed`, `cancelled`).
- Menu inventory toggle to mark items in or out of stock in real time.
- Contact inquiries inbox with read/unread status management.
- Sales summary and order analytics.

---

## Project Structure

```
comission/
├── server.py              # Flask backend server (SQLite database & REST API)
├── vercel.json            # Vercel deployment configuration
├── database/              # SQLite database storage (auto-created)
├── api/                   # PHP REST API endpoints
├── config/                # PHP database connection settings
├── controllers/           # PHP controllers
├── models/                # PHP models
├── views/                 # PHP views
├── public/
│   └── images/            # Product images and branding assets
└── frontend/              # React + TypeScript single-page application
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx        # Main application component & routing
        ├── types.ts       # TypeScript interfaces & types
        ├── components/    # UI & layout components (Menu, Cart, AdminDashboard, etc.)
        └── data/          # Menu item definitions and categories
```

---

## Getting Started

### Prerequisites
- Python 3.8+ (for Flask backend)
- Node.js 18+ and npm (for frontend development)

---

### Option 1: Python + Flask Backend (Recommended)

1. **Install Python dependencies**
   ```bash
   pip install flask
   ```

2. **Build the frontend (or run dev mode)**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Start the server**
   ```bash
   python server.py
   ```
   The application will be accessible at `http://localhost:5000`. The SQLite database and tables will initialize automatically on first start.

---

### Option 2: Frontend Development Server (Vite HMR)

For active frontend development with Hot Module Replacement:

1. **Start the Flask backend in one terminal:**
   ```bash
   python server.py
   ```

2. **Start the Vite dev server in a second terminal:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:5173`. Requests to `/api/*` will automatically proxy to the Flask backend running on port 5000.

---

### Option 3: PHP / Apache Environment (XAMPP)

1. Place the project folder inside your web root (e.g., `C:\xampp\htdocs\comission\`).
2. Create a MySQL database named `mr_boy_db` and import the schema.
3. Update database credentials in `config/database.php` if required.
4. Open `http://localhost/comission/` in your browser.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register.php` | Register a new user account |
| `POST` | `/api/login.php` | Authenticate user credentials and start session |
| `POST` | `/api/logout.php` | End current user session |
| `GET` | `/api/current_user.php` | Get currently authenticated session user |
| `POST` | `/api/update_profile.php` | Update customer profile details |
| `POST` | `/api/submit_order.php` | Submit a customer order |
| `GET` | `/api/fetch_orders.php` | Retrieve orders (admin or customer-specific) |
| `POST` | `/api/update_order_status.php` | Update order processing status |
| `POST` | `/api/delete_order.php` | Delete an order by ID |
| `POST` | `/api/clear_orders.php` | Remove all completed/cancelled orders |
| `GET` | `/api/product_availability.php` | Get stock availability states for all menu items |
| `POST` | `/api/product_availability.php` | Toggle stock availability for a specific item |
| `POST` | `/api/save_contact.php` | Submit a message through the contact form |
| `GET` | `/api/fetch_contacts.php` | Fetch customer messages (admin only) |
| `POST` | `/api/mark_contact_read.php` | Toggle read/unread flag on a contact inquiry |
| `GET` | `/api/sales_analytics.php` | Fetch sales summary and performance metrics |

---

## Store Details

- **Location**: Blk 14 Lot 4 Phase 1, Dela Costa Homes V, Burgos, Rodriguez, Rizal, Philippines 1860
- **Phone**: 0917 888 4737
- **Email**: mrboyspecialteadelacosta@gmail.com
