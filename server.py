"""
Mr. Boy SpecialTea — Flask Backend Server

Replaces the PHP backend with Python + Flask + SQLite.
Provides the same API endpoints so the frontend JS works unchanged.

Usage:
    python server.py

Then open: http://localhost:5000
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash

# ── App Configuration ──────────────────────────────────────────

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SECRET_KEY', 'mr_boy_specialtea_secret_key_2026_dev')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie, X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'database', 'mr_boy.db')

# Auto-load .env configuration if present
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception as e:
        print(f"[WARN] Error reading .env: {e}")

TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '').strip()
TURSO_AUTH_TOKEN   = os.environ.get('TURSO_AUTH_TOKEN', '').strip()


# ── Turso & SQLite Database Adapters ──────────────────────────

import requests

class TursoRow(dict):
    """Row object that supports key access, integer index access, and dict conversion."""
    def __init__(self, cols, values):
        super().__init__()
        self._cols = cols
        self._values = values
        for col, val in zip(cols, values):
            self[col] = val

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)

    def keys(self):
        return self._cols

    def values(self):
        return self._values


class TursoCursor:
    def __init__(self, cols=None, rows=None, lastrowid=None, rowcount=0):
        self._cols = cols or []
        self._rows = [TursoRow(self._cols, r) for r in (rows or [])]
        self._index = 0
        self.lastrowid = lastrowid
        self.rowcount = rowcount

    def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return row
        return None

    def fetchall(self):
        res = self._rows[self._index:]
        self._index = len(self._rows)
        return res

    def __iter__(self):
        return iter(self.fetchall())


class TursoConnection:
    """Zero-dependency pure-HTTP Turso Cloud Database connection."""
    def __init__(self, url, token):
        self.url = url.replace('libsql://', 'https://').rstrip('/') + '/v2/pipeline'
        self.token = token
        self._closed = False

    def _convert_arg(self, arg):
        if arg is None:
            return {"type": "null"}
        elif isinstance(arg, bool):
            return {"type": "integer", "value": "1" if arg else "0"}
        elif isinstance(arg, int):
            return {"type": "integer", "value": str(arg)}
        elif isinstance(arg, float):
            return {"type": "float", "value": arg}
        elif isinstance(arg, (bytes, bytearray)):
            import base64
            return {"type": "blob", "base64": base64.b64encode(arg).decode('utf-8')}
        else:
            return {"type": "text", "value": str(arg)}

    def _convert_val(self, val_obj):
        if not isinstance(val_obj, dict):
            return val_obj
        t = val_obj.get("type")
        v = val_obj.get("value")
        if t == "null":
            return None
        elif t == "integer":
            return int(v) if v is not None else None
        elif t == "float":
            return float(v) if v is not None else None
        elif t == "blob":
            import base64
            b64 = val_obj.get("base64", "")
            return base64.b64decode(b64)
        else:
            return v

    def execute(self, sql, params=()):
        if self._closed:
            raise RuntimeError("Cannot operate on closed Turso connection")
        
        args_payload = [self._convert_arg(p) for p in params]
        payload = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": sql,
                        "args": args_payload
                    }
                },
                {"type": "close"}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        resp = requests.post(self.url, headers=headers, json=payload, timeout=12)
        if resp.status_code != 200:
            raise RuntimeError(f"Turso HTTP {resp.status_code}: {resp.text}")
        
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return TursoCursor()
            
        first = results[0]
        if first.get("type") == "error":
            raise RuntimeError(f"Turso SQL Error: {first.get('error')}")
            
        response_data = first.get("response", {})
        result_data = response_data.get("result", {})
        
        cols = [c.get("name") for c in result_data.get("cols", [])]
        raw_rows = result_data.get("rows", [])
        
        parsed_rows = []
        for row in raw_rows:
            parsed_rows.append([self._convert_val(col_val) for col_val in row])
            
        last_insert_id = result_data.get("last_insert_rowid")
        if last_insert_id is not None:
            try:
                last_insert_id = int(last_insert_id)
            except (ValueError, TypeError):
                pass
                
        affected = result_data.get("affected_row_count", 0)
        return TursoCursor(cols=cols, rows=parsed_rows, lastrowid=last_insert_id, rowcount=affected)

    def executescript(self, script):
        statements = [s.strip() for s in script.split(';') if s.strip()]
        last_cur = None
        for stmt in statements:
            last_cur = self.execute(stmt)
        return last_cur

    def commit(self):
        pass

    def close(self):
        self._closed = True


def get_db():
    """Get a database connection (Turso Cloud Database if env set, otherwise local SQLite)."""
    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        try:
            return TursoConnection(TURSO_DATABASE_URL, TURSO_AUTH_TOKEN)
        except Exception as e:
            print(f"[WARN] Failed connecting to Turso ({e}). Falling back to local SQLite.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist and seed default admin."""
    if not (TURSO_DATABASE_URL and TURSO_AUTH_TOKEN):
        os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            customer_username TEXT,
            customer_email TEXT,
            order_details TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            contact TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS product_availability (
            product_id TEXT PRIMARY KEY,
            is_available INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Migration for existing orders table
    order_cols = [col[1] for col in conn.execute("PRAGMA table_info(orders)").fetchall()]
    if 'user_id' not in order_cols:
        conn.execute("ALTER TABLE orders ADD COLUMN user_id INTEGER")
    if 'customer_username' not in order_cols:
        conn.execute("ALTER TABLE orders ADD COLUMN customer_username TEXT")
    if 'customer_email' not in order_cols:
        conn.execute("ALTER TABLE orders ADD COLUMN customer_email TEXT")
    if 'status' not in order_cols:
        conn.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'pending'")

    # Migration for contact_messages table (is_read column)
    contact_cols = [col[1] for col in conn.execute("PRAGMA table_info(contact_messages)").fetchall()]
    if 'is_read' not in contact_cols:
        conn.execute("ALTER TABLE contact_messages ADD COLUMN is_read INTEGER DEFAULT 0")

    # Seed default admin if missing
    admin = conn.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if not admin:
        hashed_pw = generate_password_hash('admin123')
        conn.execute(
            "INSERT INTO users (username, email, password, fullname, role) VALUES (?, ?, ?, ?, ?)",
            ('admin', 'admin@mrboyspecialtea.com', hashed_pw, 'System Administrator', 'admin')
        )
        print("[OK] Seeded default admin account (username: admin / password: admin123)")

    conn.commit()
    conn.close()

    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        print(f"[OK] Connected to Turso Cloud Database: {TURSO_DATABASE_URL}")
    else:
        print(f"[OK] Database ready at local SQLite: {DB_PATH}")


# ── Static File Serving ───────────────────────────────────────

DIST_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

@app.route('/')
def index():
    """Serve modern React + shadcn frontend if built, or fallback to root index.html."""
    if os.path.exists(os.path.join(DIST_DIR, 'index.html')):
        return send_file(os.path.join(DIST_DIR, 'index.html'))
    return send_file(os.path.join(BASE_DIR, 'index.html'))


@app.route('/assets/<path:filename>')
def serve_dist_assets(filename):
    """Serve compiled Vite React assets."""
    return send_from_directory(os.path.join(DIST_DIR, 'assets'), filename)


@app.route('/public/<path:filename>')
def serve_public(filename):
    """Serve static media assets from public folder."""
    return send_from_directory(os.path.join(BASE_DIR, 'public'), filename)


@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve product and branding images."""
    for folder in [
        os.path.join(BASE_DIR, 'frontend', 'public', 'images'),
        os.path.join(BASE_DIR, 'public', 'images'),
        os.path.join(DIST_DIR, 'images'),
    ]:
        if os.path.exists(os.path.join(folder, filename)):
            return send_from_directory(folder, filename)
    return ('Image not found', 404)


# ── Health Check ──────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    db_type = 'turso' if (TURSO_DATABASE_URL and TURSO_AUTH_TOKEN) else 'sqlite'
    return jsonify({
        'status': 'ok',
        'database': db_type,
        'cloud_connected': bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN),
        'timestamp': datetime.utcnow().isoformat()
    })


# ── API: Auth (Register / Login / Logout / Current User) ───────

@app.route('/api/register.php', methods=['POST'])
@app.route('/api/register', methods=['POST'])
@app.route('/register.php', methods=['POST'])
@app.route('/register', methods=['POST'])
def register():
    """Register a new customer account."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    username = data.get('username', '').strip()
    fullname = data.get('fullname', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not fullname or not email or not password:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    if len(password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters.'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address.'}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Username or Email is already taken.'}), 400

    hashed_pw = generate_password_hash(password)
    cur = conn.execute(
        "INSERT INTO users (username, email, password, fullname, role) VALUES (?, ?, ?, ?, 'customer')",
        (username, email, hashed_pw, fullname)
    )
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    user_data = {
        'id': user_id,
        'username': username,
        'email': email,
        'fullname': fullname,
        'role': 'customer'
    }
    session['user'] = user_data

    return jsonify({
        'status': 'success',
        'message': 'Registration successful! Welcome to Mr. Boy SpecialTea.',
        'user': user_data
    })


@app.route('/api/login.php', methods=['POST'])
@app.route('/api/login', methods=['POST'])
@app.route('/login.php', methods=['POST'])
@app.route('/login', methods=['POST'])
def login():
    """Login with username or email."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    login_identifier = data.get('username', '').strip()
    password         = data.get('password', '')

    if not login_identifier or not password:
        return jsonify({'status': 'error', 'message': 'Username/Email and Password are required.'}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT id, username, email, password, fullname, role FROM users WHERE username = ? OR email = ?",
        (login_identifier, login_identifier.lower())
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'status': 'error', 'message': 'Invalid username/email or password.'}), 401

    user_data = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'fullname': user['fullname'],
        'role': user['role']
    }
    session['user'] = user_data

    return jsonify({
        'status': 'success',
        'message': f'Welcome back, {user["fullname"]}!',
        'user': user_data
    })


@app.route('/api/logout.php', methods=['POST', 'GET'])
@app.route('/api/logout', methods=['POST', 'GET'])
@app.route('/logout.php', methods=['POST', 'GET'])
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Log out current user."""
    session.pop('user', None)
    return jsonify({'status': 'success', 'message': 'Logged out successfully.'})


@app.route('/api/current_user.php', methods=['GET'])
@app.route('/api/current_user', methods=['GET'])
@app.route('/current_user.php', methods=['GET'])
@app.route('/current_user', methods=['GET'])
def current_user():
    """Get current session user."""
    user = session.get('user')
    if user:
        return jsonify({'logged_in': True, 'user': user})
    return jsonify({'logged_in': False, 'user': None})


@app.route('/api/change_password.php', methods=['POST'])
@app.route('/api/change_password', methods=['POST'])
@app.route('/change_password.php', methods=['POST'])
@app.route('/change_password', methods=['POST'])
def change_password():
    """Change user password after verifying current password."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    session_user = session.get('user')
    user_id = data.get('user_id') or (session_user.get('id') if session_user else None)
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not user_id:
        return jsonify({'status': 'error', 'message': 'You must be logged in to change your password.'}), 401

    if not current_password or not new_password:
        return jsonify({'status': 'error', 'message': 'Both current and new password are required.'}), 400

    if len(new_password) < 6:
        return jsonify({'status': 'error', 'message': 'New password must be at least 6 characters long.'}), 400

    conn = get_db()
    user = conn.execute("SELECT id, password, fullname, username FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        conn.close()
        return jsonify({'status': 'error', 'message': 'User account not found.'}), 404

    if not check_password_hash(user['password'], current_password):
        conn.close()
        return jsonify({'status': 'error', 'message': 'Current password is incorrect. Please try again.'}), 400

    if current_password == new_password:
        conn.close()
        return jsonify({'status': 'error', 'message': 'New password cannot be the same as your old password.'}), 400

    hashed_pw = generate_password_hash(new_password)
    conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Password changed successfully! You can now use your new password.'
    })


# ── API: Orders ───────────────────────────────────────────────

@app.route('/api/submit_order.php', methods=['POST'])
@app.route('/api/submit_order', methods=['POST'])
@app.route('/submit_order.php', methods=['POST'])
@app.route('/submit_order', methods=['POST'])
def submit_order():
    """Create a new order bound strictly to authenticated user credentials."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    # Verify user authentication via session or verified user_id
    session_user = session.get('user')
    user_id = data.get('user_id')

    conn = get_db()

    authenticated_user = None
    if session_user and session_user.get('id'):
        user_row = conn.execute("SELECT id, fullname, username, email, role FROM users WHERE id = ?", (session_user['id'],)).fetchone()
        if user_row:
            authenticated_user = dict(user_row)
    elif user_id:
        user_row = conn.execute("SELECT id, fullname, username, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
        if user_row:
            authenticated_user = dict(user_row)

    if not authenticated_user:
        conn.close()
        return jsonify({
            'status': 'error',
            'message': 'You must be logged in to submit an order.',
            'require_auth': True
        }), 401

    # Bind order to authenticated user credentials
    bound_user_id = authenticated_user['id']
    customer_name = authenticated_user['fullname']
    customer_username = authenticated_user['username']
    customer_email = authenticated_user['email']
    order_details = data.get('order_details', '').strip()
    total_price   = float(data.get('total_price', 0))

    if not order_details or total_price <= 0:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Cart is empty or missing order details.'}), 400

    cursor = conn.execute(
        '''INSERT INTO orders (user_id, customer_name, customer_username, customer_email, order_details, total_price, status)
           VALUES (?, ?, ?, ?, ?, ?, 'pending')''',
        (bound_user_id, customer_name, customer_username, customer_email, order_details, total_price)
    )
    new_order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': f'Order #{new_order_id} successfully bound to account @{customer_username}!',
        'order_id': new_order_id
    })


@app.route('/api/fetch_orders.php', methods=['GET'])
@app.route('/api/fetch_orders', methods=['GET'])
@app.route('/fetch_orders.php', methods=['GET'])
@app.route('/fetch_orders', methods=['GET'])
def fetch_orders():
    """Fetch orders. If user_id provided, filter by user; otherwise return all."""
    user_id_param = request.args.get('user_id')
    conn = get_db()

    if user_id_param:
        rows = conn.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', 
            (user_id_param,)
        ).fetchall()
    else:
        rows = conn.execute('SELECT * FROM orders ORDER BY order_date DESC').fetchall()
    
    conn.close()

    orders = []
    for row in rows:
        orders.append({
            'id': row['id'],
            'user_id': row['user_id'] if 'user_id' in row.keys() else None,
            'customer_name': row['customer_name'],
            'customer_username': row['customer_username'] if 'customer_username' in row.keys() else None,
            'customer_email': row['customer_email'] if 'customer_email' in row.keys() else None,
            'order_details': row['order_details'],
            'total_price': row['total_price'],
            'status': row['status'] if 'status' in row.keys() else 'pending',
            'order_date': row['order_date'],
        })

    return jsonify(orders)


@app.route('/api/update_order_status.php', methods=['POST'])
@app.route('/api/update_order_status', methods=['POST'])
@app.route('/update_order_status.php', methods=['POST'])
@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    """Update order status (pending / completed)."""
    data = request.get_json() or {}
    order_id = data.get('id', 0)
    status = data.get('status', 'completed')

    if not order_id:
        return jsonify({'status': 'error', 'message': 'Invalid order ID.'}), 400

    conn = get_db()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': f'Order #{order_id} marked as {status}.'})


@app.route('/api/delete_order.php', methods=['POST'])
@app.route('/api/delete_order', methods=['POST'])
@app.route('/delete_order.php', methods=['POST'])
@app.route('/delete_order', methods=['POST'])
def delete_order():
    """Delete a single order by ID."""
    data = request.get_json()
    order_id = data.get('id', 0) if data else 0

    if not order_id:
        return jsonify({'status': 'error', 'message': 'Invalid order ID.'}), 400

    conn = get_db()
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Order deleted.'})


@app.route('/api/clear_orders.php', methods=['POST'])
@app.route('/api/clear_orders', methods=['POST'])
@app.route('/clear_orders.php', methods=['POST'])
@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    """Delete all orders."""
    conn = get_db()
    conn.execute('DELETE FROM orders')
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'All orders cleared.'})


# ── API: Contact ──────────────────────────────────────────────

@app.route('/api/save_contact.php', methods=['POST'])
@app.route('/api/save_contact', methods=['POST'])
@app.route('/save_contact.php', methods=['POST'])
@app.route('/save_contact', methods=['POST'])
def save_contact():
    """Save a contact form message (supports both JSON and form data)."""
    is_json = request.is_json or request.content_type == 'application/json'
    if is_json:
        data = request.get_json() or {}
        name    = data.get('name', '').strip()
        email   = data.get('email', '').strip()
        contact = data.get('contact', '').strip()
        message = data.get('message', '').strip()
    else:
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        contact = request.form.get('contact', '').strip()
        message = request.form.get('message', '').strip()

    if not name or not email or not message:
        if is_json:
            return jsonify({'status': 'error', 'message': 'Please fill in all required fields.'}), 400
        return '''<script>
            alert("Please fill in all required fields.");
            window.history.back();
        </script>'''

    conn = get_db()
    conn.execute(
        'INSERT INTO contact_messages (name, email, contact, message) VALUES (?, ?, ?, ?)',
        (name, email, contact, message)
    )
    conn.commit()
    conn.close()

    if is_json:
        return jsonify({'status': 'success', 'message': 'Thank you! Your message has been sent.'})


# ── API: Product Availability ─────────────────────────────────

@app.route('/api/product_availability.php', methods=['GET'])
@app.route('/api/product_availability', methods=['GET'])
@app.route('/product_availability.php', methods=['GET'])
@app.route('/product_availability', methods=['GET'])
def get_product_availability():
    """Fetch availability status of all products."""
    conn = get_db()
    rows = conn.execute('SELECT product_id, is_available FROM product_availability').fetchall()
    conn.close()

    availability = {}
    for row in rows:
        availability[row['product_id']] = bool(row['is_available'])

    return jsonify(availability)


@app.route('/api/toggle_product_availability.php', methods=['POST'])
@app.route('/api/toggle_product_availability', methods=['POST'])
@app.route('/toggle_product_availability.php', methods=['POST'])
@app.route('/toggle_product_availability', methods=['POST'])
def toggle_product_availability():
    """Toggle or set product availability status (1 = Available, 0 = Sold Out)."""
    data = request.get_json() or {}
    product_id = data.get('product_id', '').strip()
    is_available = data.get('is_available', True)

    if not product_id:
        return jsonify({'status': 'error', 'message': 'Product ID is required.'}), 400

    int_val = 1 if is_available else 0
    conn = get_db()
    conn.execute(
        '''INSERT INTO product_availability (product_id, is_available, updated_at)
           VALUES (?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(product_id) DO UPDATE SET is_available = excluded.is_available, updated_at = CURRENT_TIMESTAMP''',
        (product_id, int_val)
    )
    conn.commit()
    conn.close()

    status_text = 'available' if is_available else 'sold out / unavailable'
    return jsonify({
        'status': 'success',
        'message': f'Product "{product_id}" is now marked as {status_text}.',
        'product_id': product_id,
        'is_available': bool(is_available)
    })


# ── API: Contact Messages Fetch, Read Status & Delete ────────

@app.route('/api/fetch_contacts.php', methods=['GET'])
@app.route('/api/fetch_contacts', methods=['GET'])
@app.route('/fetch_contacts.php', methods=['GET'])
@app.route('/fetch_contacts', methods=['GET'])
def fetch_contacts():
    """Fetch all submitted customer contact inquiries."""
    conn = get_db()
    rows = conn.execute('SELECT * FROM contact_messages ORDER BY created_at DESC').fetchall()
    conn.close()

    contacts = []
    for r in rows:
        contacts.append({
            'id': r['id'],
            'name': r['name'],
            'email': r['email'],
            'contact': r['contact'],
            'message': r['message'],
            'is_read': bool(r['is_read']) if 'is_read' in r.keys() else False,
            'created_at': r['created_at'],
        })

    return jsonify(contacts)


@app.route('/api/mark_contact_read.php', methods=['POST'])
@app.route('/api/mark_contact_read', methods=['POST'])
@app.route('/mark_contact_read.php', methods=['POST'])
@app.route('/mark_contact_read', methods=['POST'])
def mark_contact_read():
    """Mark a contact message (or all) as read/unread."""
    data = request.get_json() or {}
    conn = get_db()

    if data.get('mark_all'):
        conn.execute('UPDATE contact_messages SET is_read = 1')
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'All contact messages marked as read.'})

    message_id = data.get('id')
    is_read = data.get('is_read', True)

    if not message_id:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Invalid message ID.'}), 400

    int_val = 1 if is_read else 0
    conn.execute('UPDATE contact_messages SET is_read = ? WHERE id = ?', (int_val, message_id))
    conn.commit()
    conn.close()

    read_label = 'read' if is_read else 'unread'
    return jsonify({
        'status': 'success',
        'message': f'Message #{message_id} marked as {read_label}.',
        'id': message_id,
        'is_read': bool(is_read)
    })


@app.route('/api/delete_contact.php', methods=['POST'])
@app.route('/api/delete_contact', methods=['POST'])
@app.route('/delete_contact.php', methods=['POST'])
@app.route('/delete_contact', methods=['POST'])
def delete_contact():
    """Delete a contact message by ID."""
    data = request.get_json() or {}
    message_id = data.get('id')

    if not message_id:
        return jsonify({'status': 'error', 'message': 'Invalid message ID.'}), 400

    conn = get_db()
    conn.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': f'Contact message #{message_id} deleted.'})


# ── API: Sales Analytics ──────────────────────────────────────

@app.route('/api/sales_analytics.php', methods=['GET'])
@app.route('/api/sales_analytics', methods=['GET'])
@app.route('/sales_analytics.php', methods=['GET'])
@app.route('/sales_analytics', methods=['GET'])
def sales_analytics():
    """Comprehensive sales analytics for admin dashboard."""
    conn = get_db()

    # Total orders & gross revenue
    total_row = conn.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total FROM orders WHERE status != 'cancelled'"
    ).fetchone()
    all_orders_count = conn.execute("SELECT COUNT(*) as count FROM orders").fetchone()['count']

    today_row = conn.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total FROM orders WHERE DATE(order_date) = DATE('now') AND status != 'cancelled'"
    ).fetchone()

    month_row = conn.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(total_price), 0) as total FROM orders "
        "WHERE strftime('%m', order_date) = strftime('%m', 'now') "
        "AND strftime('%Y', order_date) = strftime('%Y', 'now') AND status != 'cancelled'"
    ).fetchone()

    # Status counts
    status_rows = conn.execute(
        "SELECT status, COUNT(*) as count, COALESCE(SUM(total_price), 0) as revenue FROM orders GROUP BY status"
    ).fetchall()

    status_counts = {'pending': 0, 'received': 0, 'completed': 0, 'cancelled': 0}
    status_revenue = {'pending': 0.0, 'received': 0.0, 'completed': 0.0, 'cancelled': 0.0}

    for sr in status_rows:
        s = sr['status'] or 'pending'
        status_counts[s] = sr['count']
        status_revenue[s] = float(sr['revenue'])

    # Parse best selling items from non-cancelled order_details
    order_details_rows = conn.execute(
        "SELECT order_details, total_price FROM orders WHERE status != 'cancelled'"
    ).fetchall()

    item_popularity = {}
    for od in order_details_rows:
        raw_text = od['order_details'] or ''
        parts = [p.strip() for p in raw_text.split(',') if p.strip()]
        for p in parts:
            # Extract main name before parentheses
            main_name = p.split('(')[0].strip()
            if main_name:
                item_popularity[main_name] = item_popularity.get(main_name, 0) + 1

    sorted_items = sorted(
        [{'name': k, 'count': v} for k, v in item_popularity.items()],
        key=lambda x: x['count'],
        reverse=True
    )[:10]

    # Recent orders summary
    recent_orders = conn.execute(
        "SELECT id, customer_name, total_price, status, order_date FROM orders ORDER BY order_date DESC LIMIT 5"
    ).fetchall()

    recent_list = []
    for ro in recent_orders:
        recent_list.append({
            'id': ro['id'],
            'customer_name': ro['customer_name'],
            'total_price': ro['total_price'],
            'status': ro['status'],
            'order_date': ro['order_date']
        })

    conn.close()

    total_gross = float(total_row['total'])
    valid_count = int(total_row['count'])
    aov = (total_gross / valid_count) if valid_count > 0 else 0.0

    return jsonify({
        'status': 'success',
        'total_revenue': total_gross,
        'total_orders': all_orders_count,
        'valid_orders_count': valid_count,
        'average_order_value': round(aov, 2),
        'today': {
            'revenue': float(today_row['total']),
            'orders': int(today_row['count'])
        },
        'this_month': {
            'revenue': float(month_row['total']),
            'orders': int(month_row['count'])
        },
        'status_breakdown': {
            'counts': status_counts,
            'revenue': status_revenue
        },
        'top_selling_items': sorted_items,
        'recent_activity': recent_list
    })


# ── Main ──────────────────────────────────────────────────────

try:
    init_db()
except Exception as e:
    print(f"[WARN] Database initialization notice: {e}")

if __name__ == '__main__':
    print()
    print("== Mr. Boy SpecialTea Server ==")
    print("   http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print()
    app.run(debug=True, port=5000)
