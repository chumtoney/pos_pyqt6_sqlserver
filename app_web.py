from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pos_super_secret_key'

# ១. ទិន្នន័យគំរូសម្រាប់ប្រព័ន្ធដំណើរការ (Mock Database)
USER_DATA = {"admin": "1234"}

# បញ្ជីផលិតផលដកស្រង់លំនាំតាមវីដេអូរបស់អ្នក
if 'products' not in session:
    PRODUCTS_DB = [
        {"id": 1, "name": "Pen", "price": 1.50, "stock": 100, "category": "Stationary"},
        {"id": 2, "name": "Notebook", "price": 2.75, "stock": 80, "category": "Stationary"},
        {"id": 3, "name": "USB 16GB", "price": 6.90, "stock": 40, "category": "Electronic"},
        {"id": 4, "name": "Banana", "price": 2.00, "stock": 2, "category": "None"},
        {"id": 16, "name": "Apple", "price": 7.00, "stock": 2, "category": "Stationary"}
    ]
else:
    PRODUCTS_DB = []

SALES_HISTORY = [
    {"sale_id": 1, "total": 21.00, "date": "2026-03-04 14:20"}
]

# ២. ផ្ទាំង LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USER_DATA and USER_DATA[username] == password:
            session['user'] = username
            return redirect(url_for('products_page'))
        else:
            flash("Username ឬ Password មិនត្រឹមត្រូវទេ!", "error")
    
    return render_template_string("""
    <html>
    <head>
        <title>POS System - Login</title>
        <style>
            body { font-family: 'Segoe UI', 'Khmer OS Battambang'; background: #1e1e24; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: white; }
            .login-box { background: #2a2a35; padding: 40px; border-radius: 8px; width: 320px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #444; background: #1e1e24; color: white; border-radius: 4px; }
            button { width: 100%; padding: 10px; background: #007bff; border: none; color: white; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #0056b3; }
            .error { color: #ff6b6b; text-align: center; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2 style="text-align:center;">🔐 POS SYSTEM LOGIN</h2>
            {% with messages = get_flashed_messages() %}
                {% if messages %}{% for m in messages %}<p class="error">{{m}}</p>{% endfor %}{% endif %}
            {% endwith %}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ៣. ផ្ទាំង PRODUCTS (CRUD)
@app.route('/products', methods=['GET', 'POST'])
def products_page():
    if 'user' not in session: return redirect(url_for('login'))
    global PRODUCTS_DB
    
    if request.method == 'POST' and 'add_product' in request.form:
        name = request.form.get('name')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category = request.form.get('category')
        new_id = max([p['id'] for p in PRODUCTS_DB]) + 1 if PRODUCTS_DB else 1
        PRODUCTS_DB.append({"id": new_id, "name": name, "price": price, "stock": stock, "category": category})
        return redirect(url_for('products_page'))

    return render_template_string(get_main_layout("products"), list_data=PRODUCTS_DB)

# ៤. ផ្ទាំង SALES (ការលក់ចេញ)
@app.route('/sales', methods=['GET', 'POST'])
def sales_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(get_main_layout("sales"), list_data=PRODUCTS_DB)

# ៥. ផ្ទាំង SALES HISTORY
@app.route('/history')
def history_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(get_main_layout("history"), list_data=SALES_HISTORY)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ៦. ផ្ទាំង Layout រួម (រចនាពណ៌ក្រម៉ៅលំនាំតាម PyQt6 របស់អ្នក)
def get_main_layout(active_tab):
    return f"""
    <html>
    <head>
        <title>POS System</title>
        <style>
            body {{ font-family: 'Segoe UI', 'Khmer OS Battambang'; margin: 0; background: #202026; color: #fff; }}
            .navbar {{ background: #2d2d37; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3e3e4f; }}
            .tabs a {{ color: #aaa; text-decoration: none; padding: 10px 20px; margin-right: 5px; background: #25252f; border-radius: 4px 4px 0 0; }}
            .tabs a.active {{ color: #fff; background: #007bff; font-weight: bold; }}
            .container {{ padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background: #2d2d37; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #3e3e4f; }}
            th {{ background: #25252f; color: #007bff; }}
            .form-inline {{ background: #2d2d37; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
            input, select {{ padding: 8px; margin-right: 10px; background: #202026; color: white; border: 1px solid #444; border-radius: 4px; }}
            .btn {{ padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .btn-danger {{ background: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <div class="tabs">
                <a href="/products" class="{'active' if active_tab=='products' else ''}">Products</a>
                <a href="/sales" class="{'active' if active_tab=='sales' else ''}">Sales</a>
                <a href="/history" class="{'active' if active_tab=='history' else ''}">Sales History</a>
            </div>
            <div>
                <span>Logged in as: <strong>Admin</strong></span> | 
                <a href="/logout" style="color: #ff6b6b; text-decoration: none;">Logout</a>
            </div>
        </div>
        <div class="container">
            {" " if active_tab != 'products' else \"\"\"
                <h3>➕ Add New Product</h3>
                <form class="form-inline" method="POST">
                    <input type="hidden" name="add_product" value="1">
                    <input type="text" name="name" placeholder="Product Name" required>
                    <input type="number" step="0.01" name="price" placeholder="Price ($)" required>
                    <input type="number" name="stock" placeholder="Stock" required>
                    <select name="category">
                        <option value="None">None</option>
                        <option value="Stationary">Stationary</option>
                        <option value="Electronic">Electronic</option>
                    </select>
                    <button type="submit" class="btn">Add Product</button>
                </form>
            \"\"\"}
            
            <h3>📋 Content Data</h3>
            <table>
                {get_table_content(active_tab)}
            </table>
        </div>
    </body>
    </html>
    """

def get_table_content(tab):
    if tab == "products" or tab == "sales":
        return """
        <tr><th>ID</th><th>Name</th><th>Price</th><th>Stock</th><th>Category</th></tr>
        {% for p in list_data %}
        <tr><td>{{p.id}}</td><td>{{p.name}}</td><td>${{p.price}}</td><td>{{p.stock}}</td><td>{{p.category}}</td></tr>
        {% endfor %}
        """
    else:
        return """
        <tr><th>Sale ID</th><th>Total Amount</th><th>Date Time</th></tr>
        {% for h in list_data %}
        <tr><td>{{h.sale_id}}</td><td>${{h.total}}</td><td>{{h.date}}</td></tr>
        {% endfor %}
        """

if __name__ == '__main__':
    app.run(debug=True)