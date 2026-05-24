from flask import Flask, render_template_string, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'pos_secret_key_999'

# ==========================================
# ១. ទិន្នន័យបណ្តោះអាសន្ន (Mock Database)
# ==========================================
USER_DATA = {"admin": "1234"}

PRODUCTS_DB = [
    {"id": 1, "name": "Pen", "price": 1.50, "stock": 100, "category": "Stationary"},
    {"id": 2, "name": "Notebook", "price": 2.75, "stock": 80, "category": "Stationary"},
    {"id": 3, "name": "USB 16GB", "price": 6.90, "stock": 40, "category": "Electronic"},
    {"id": 4, "name": "Banana", "price": 2.00, "stock": 2, "category": "None"},
    {"id": 16, "name": "Apple", "price": 7.00, "stock": 2, "category": "Stationary"}
]

SALES_HISTORY = [
    {"sale_id": 1, "total": 21.00, "date": "2026-05-16 14:20"},
    {"sale_id": 2, "total": 13.50, "date": "2026-05-24 10:15"}
]

# ==========================================
# ២. មុខងារបញ្ជារត់ (Backend Logic Routes)
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USER_DATA and USER_DATA[username] == password:
            session['user'] = username
            return redirect(url_for('products_page'))
        else:
            flash("ឈ្មោះអ្នកប្រើប្រាស់ ឬ លេខសម្ងាត់មិនត្រឹមត្រូវទេ!", "error")
    
    return render_template_string("""
    <html>
    <head>
        <title>POS System - Login</title>
        <style>
            body { font-family: 'Segoe UI', 'Khmer OS Battambang'; background: #1e1e24; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: white; }
            .login-box { background: #2a2a35; padding: 40px; border-radius: 8px; width: 320px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            h2 { text-align: center; color: #007bff; margin-bottom: 25px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #444; background: #1e1e24; color: white; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #007bff; border: none; color: white; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 10px; }
            button:hover { background: #0056b3; }
            .error { color: #ff6b6b; text-align: center; font-size: 14px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>🔐 ប្រព័ន្ធគ្រប់គ្រង POS</h2>
            {% with messages = get_flashed_messages() %}
                {% if messages %}{% for m in messages %}<p class="error">{{m}}</p>{% endfor %}{% endif %}
            {% endwith %}
            <form method="POST">
                <input type="text" name="username" placeholder="ឈ្មោះអ្នកប្រើប្រាស់ (admin)" required>
                <input type="password" name="password" placeholder="លេខសម្ងាត់ (1234)" required>
                <button type="submit">ចូលប្រើប្រាស់</button>
            </form>
        </div>
    </body>
    </html>
    """)

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
    
    if request.method == 'POST' and 'delete_id' in request.form:
        del_id = int(request.form.get('delete_id'))
        PRODUCTS_DB = [p for p in PRODUCTS_DB if p['id'] != del_id]
        return redirect(url_for('products_page'))

    return render_template_string(HTML_LAYOUT, active_tab="products", list_data=PRODUCTS_DB)

@app.route('/sales')
def sales_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(HTML_LAYOUT, active_tab="sales", list_data=PRODUCTS_DB)

@app.route('/history')
def history_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(HTML_LAYOUT, active_tab="history", list_data=SALES_HISTORY)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ==========================================
# ៣. ផ្ទៃរចនា និង قالبរួម (HTML/CSS Standard Layout)
# ==========================================
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>POS System - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', 'Khmer OS Battambang'; margin: 0; background: #1e1e24; color: #fff; }
        .navbar { background: #2a2a35; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3e3e4f; }
        .tabs a { color: #aaa; text-decoration: none; padding: 12px 25px; margin-right: 5px; background: #25252f; border-radius: 6px 6px 0 0; display: inline-block; transition: 0.3s; }
        .tabs a.active { color: #fff; background: #007bff; font-weight: bold; }
        .tabs a:hover { background: #3e3e4f; color: white; }
        .container { padding: 30px; max-width: 1100px; margin: 0 auto; }
        table { width: 100%; border-collapse: collapse; background: #2a2a35; margin-top: 20px; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        th, td { padding: 14px; text-align: left; border-bottom: 1px solid #3e3e4f; }
        th { background: #25252f; color: #007bff; font-size: 15px; }
        tr:hover { background: #333344; }
        .form-inline { background: #2a2a35; padding: 20px; border-radius: 6px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        input, select { padding: 10px; margin-right: 12px; background: #1e1e24; color: white; border: 1px solid #444; border-radius: 4px; font-size: 14px; }
        .btn { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn:hover { background: #218838; }
        .btn-danger { background: #dc3545; padding: 6px 12px; font-size: 13px; }
        .btn-danger:hover { background: #c82333; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="tabs">
            <a href="/products" class="{% if active_tab == 'products' %}active{% endif %}">📦 Products (ទំនិញ)</a>
            <a href="/sales" class="{% if active_tab == 'sales' %}active{% endif %}">🛒 Sales (ការលក់)</a>
            <a href="/history" class="{% if active_tab == 'history' %}active{% endif %}">📜 Sales History (ប្រវត្តិ)</a>
        </div>
        <div>
            <span style="margin-right: 15px;">អ្នកប្រើប្រាស់: <strong style="color:#28a745;">Admin</strong></span>
            <a href="/logout" style="color: #ff6b6b; text-decoration: none; font-weight: bold; background: #3e3e4f; padding: 8px 15px; border-radius: 4px;">ចាកចេញ</a>
        </div>
    </div>
    <div class="container">
        
        {% if active_tab == 'products' %}
            <h3 style="color: #007bff; margin-top: 0;">➕ បន្ថែមផលិតផលថ្មី (Add Product)</h3>
            <form class="form-inline" method="POST">
                <input type="hidden" name="add_product" value="1">
                <input type="text" name="name" placeholder="ឈ្មោះទំនិញ" required>
                <input type="number" step="0.01" name="price" placeholder="តម្លៃ ($)" required>
                <input type="number" name="stock" placeholder="ចំនួនក្នុងស្តុក" required>
                <select name="category">
                    <option value="None">None</option>
                    <option value="Stationary">Stationary</option>
                    <option value="Electronic">Electronic</option>
                </select>
                <button type="submit" class="btn">រក្សាទុក</button>
            </form>
        {% endif %}
        
        <h3 style="color: #007bff;">📋 បញ្ជីទិន្នន័យបង្ហាញលើប្រព័ន្ធ (POS Data)</h3>
        <table>
            {% if active_tab == 'products' %}
                <tr><th>លេខកូដ (ID)</th><th>ឈ្មោះទំនិញ (Name)</th><th>តម្លៃ (Price)</th><th>ចំនួនស្តុក (Stock)</th><th>ប្រភេទ (Category)</th><th>សកម្មភាព</th></tr>
                {% for p in list_data %}
                <tr>
                    <td>{{p.id}}</td>
                    <td><strong>{{p.name}}</strong></td>
                    <td style="color:#28a745; font-weight:bold;">${{p.price}}</td>
                    <td>{{p.stock}} ដើម/កំប៉ុង</td>
                    <td><span style="background:#25252f; padding:4px 8px; border-radius:4px;">{{p.category}}</span></td>
                    <td>
                        <form method="POST" style="margin:0;">
                            <input type="hidden" name="delete_id" value="{{p.id}}">
                            <button type="submit" class="btn btn-danger">លុប</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}

            {% elif active_tab == 'sales' %}
                <tr><th>លេខកូដ (ID)</th><th>ឈ្មោះទំនិញ (Name)</th><th>តម្លៃ (Price)</th><th>ចំនួនស្តុកដែលនៅសល់</th><th>សកម្មភាពលក់</th></tr>
                {% for p in list_data %}
                <tr>
                    <td>{{p.id}}</td>
                    <td><strong>{{p.name}}</strong></td>
                    <td style="color:#28a745;">${{p.price}}</td>
                    <td>{{p.stock}}</td>
                    <td><button class="btn" style="padding: 5px 10px; font-size:13px;">🛒 លក់ចេញ (Sell)</button></td>
                </tr>
                {% endfor %}

            {% else %}
                <tr><th>លេខរៀងវិក្កយបត្រ (Sale ID)</th><th>ទឹកប្រាក់សរុប (Total Amount)</th><th>កាលបរិច្ឆេទលក់ (Date Time)</th></tr>
                {% for h in list_data %}
                <tr>
                    <td>#000{{h.sale_id}}</td>
                    <td style="color:#28a745; font-weight:bold;">${{h.total}}</td>
                    <td style="color:#aaa;">{{h.date}}</td>
                </tr>
                {% endfor %}
            {% endif %}
        </table>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)