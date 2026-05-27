from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from datetime import datetime

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
            flash("Invalid username or password!", "error")
    
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
            <h2>🔐Login System POS</h2>
            {% with messages = get_flashed_messages() %}
                {% if messages %}{% for m in messages %}<p class="error">{{m}}</p>{% endfor %}{% endif %}
            {% endwith %}
            <form method="POST">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter your username" required>
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter your password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route('/products', methods=['GET', 'POST'])
def products_page():
    if 'user' not in session: return redirect(url_for('login'))
    global PRODUCTS_DB
    
    if request.method == 'POST':
        if 'add_product' in request.form:
            name = request.form.get('name')
            price = float(request.form.get('price'))
            stock = int(request.form.get('stock'))
            category = request.form.get('category')
            new_id = max([p['id'] for p in PRODUCTS_DB]) + 1 if PRODUCTS_DB else 1
            PRODUCTS_DB.append({"id": new_id, "name": name, "price": price, "stock": stock, "category": category})
            flash("🎨 បន្ថែមទំនិញថ្មីបានជោគជ័យ!", "success")
            return redirect(url_for('products_page'))
        
        elif 'update_product' in request.form:
            p_id = int(request.form.get('id'))
            for p in PRODUCTS_DB:
                if p['id'] == p_id:
                    p['name'] = request.form.get('name')
                    p['price'] = float(request.form.get('price'))
                    p['stock'] = int(request.form.get('stock'))
                    p['category'] = request.form.get('category')
                    break
            flash("📝 ធ្វើបច្ចុប្បន្នភាពទំនិញរួចរាល់!", "success")
            return redirect(url_for('products_page'))
        
        elif 'delete_id' in request.form:
            del_id = int(request.form.get('delete_id'))
            PRODUCTS_DB = [p for p in PRODUCTS_DB if p['id'] != del_id]
            flash("🗑️ លុបទំនិញចេញពីប្រព័ន្ធរួចរាល់!", "success")
            return redirect(url_for('products_page'))

    return render_template_string(HTML_LAYOUT, active_tab="products", list_data=PRODUCTS_DB)

@app.route('/sales')
def sales_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(HTML_LAYOUT, active_tab="sales", list_data=PRODUCTS_DB)

# API Route សម្រាប់ទទួលទិន្នន័យCheckout (គិតលុយ) និងកាត់ស្តុក
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    global PRODUCTS_DB, SALES_HISTORY
    data = request.get_json()
    cart = data.get('cart', [])
    
    if not cart:
        return jsonify({"success": False, "message": "កន្ត្រកទំនិញទំនេរទទេ!"})
    
    # ពិនិត្យស្តុកមុនពេលកាត់ទាត់ទិន្នន័យ
    for item in cart:
        for p in PRODUCTS_DB:
            if p['id'] == item['id']:
                if p['stock'] < item['qty']:
                    return jsonify({"success": False, "message": f"ទំនិញ '{p['name']}' មិនមានស្តុកគ្រប់គ្រាន់ទេ! (នៅសល់ {p['stock']})"})
    
    # ដំណើរការកាត់ស្តុក និងគណនាតម្លៃសរុប
    total_bill = 0.0
    for item in cart:
        for p in PRODUCTS_DB:
            if p['id'] == item['id']:
                p['stock'] -= item['qty']  # កាត់ស្តុកចេញ
                total_bill += p['price'] * item['qty']
    
    # បន្ថែមចូលទៅក្នុងប្រវត្តិនៃការលក់
    new_sale_id = max([s['sale_id'] for s in SALES_HISTORY]) + 1 if SALES_HISTORY else 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    SALES_HISTORY.append({
        "sale_id": new_sale_id,
        "total": round(total_bill, 2),
        "date": now_str
    })
    
    flash(f"🛒 លក់ចេញបានជោគជ័យ! វិក្កយបត្រ #{new_sale_id} សរុប ${round(total_bill, 2)}", "success")
    return jsonify({"success": True})

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
        .container { padding: 30px; max-width: 1350px; margin: 0 auto; }
        
        .form-inline { 
            background: #2a2a35; 
            padding: 15px 20px; 
            border-radius: 6px; 
            margin-bottom: 25px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.2); 
            display: flex; 
            flex-direction: row;
            flex-wrap: nowrap; 
            gap: 10px; 
            align-items: center;
            overflow-x: auto;
        }
        
        .form-inline input, .form-inline select { 
            padding: 10px; 
            background: #1e1e24; 
            color: white; 
            border: 1px solid #444; 
            border-radius: 4px; 
            font-size: 14px;
            flex: 1; 
            min-width: 120px;
        }
        
        .btn { padding: 10px 18px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s; white-space: nowrap; font-size: 14px; }
        .btn:hover { background: #218838; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-warning:hover { background: #e0a800; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-danger:hover { background: #c82333; }
        .btn-info { background: #17a2b8; color: white; }
        .btn-info:hover { background: #138496; }
        .btn-secondary { background: #6c757d; color: white; }
        
        table { width: 100%; border-collapse: collapse; background: #2a2a35; margin-top: 20px; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        th, td { padding: 14px; text-align: left; border-bottom: 1px solid #3e3e4f; }
        th { background: #25252f; color: #007bff; font-size: 15px; }
        tr:hover { background: #333344; }
        
        .alert { padding: 12px; background: #28a745; color: white; border-radius: 4px; margin-bottom: 15px; font-weight: bold; }

        .modal { display: none; position: fixed; z-index: 100; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; }
        .modal-content { background: #2a2a35; padding: 30px; border-radius: 8px; width: 350px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
        .modal-content h3 { margin-top: 0; color: #ffc107; }
        .modal-content label { display: block; margin-top: 10px; font-size: 14px; color: #aaa; }
        .modal-content input, .modal-content select { width: 100%; margin-top: 5px; box-sizing: border-box; }
        .modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

        /* រចនាបថចែកជាពីរជួរលើទំព័រលក់ (Sales Page Split Layout) */
        .sales-container { display: flex; gap: 20px; align-items: flex-start; }
        .products-side { flex: 7; }
        .cart-side { flex: 4; background: #2a2a35; padding: 20px; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
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
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}{% for m in messages %}<div class="alert">{{m}}</div>{% endfor %}{% endif %}
        {% endwith %}
        
        {% if active_tab == 'products' %}
            <h3 style="color: #007bff; margin-top: 0;">➕ Add Product (បន្ថែមផលិតផលថ្មី)</h3>
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
                
                <button type="submit" class="btn">💾 Save</button>
                <button type="button" class="btn btn-info" onclick="window.location.reload();">🔄 Refresh</button>
            </form>

            <h3 style="color: #007bff;">📋 បញ្ជីទិន្នន័យបង្ហាញលើប្រព័ន្ធ (POS Data)</h3>
            <table>
                <tr><th>លេខកូដ (ID)</th><th>ឈ្មោះទំនិញ (Name)</th><th>តម្លៃ (Price)</th><th>ចំនួនស្តុក (Stock)</th><th>ប្រភេទ (Category)</th><th style="text-align:center;">សកម្មភាពបញ្ជា</th></tr>
                {% for p in list_data %}
                <tr>
                    <td>{{p.id}}</td>
                    <td><strong>{{p.name}}</strong></td>
                    <td style="color:#28a745; font-weight:bold;">${{p.price}}</td>
                    <td>{{p.stock}} ដើម/កំប៉ុង</td>
                    <td><span style="background:#25252f; padding:4px 8px; border-radius:4px;">{{p.category}}</span></td>
                    <td style="text-align:center; display: flex; justify-content: center; gap: 8px;">
                        <button class="btn btn-warning" style="padding: 6px 12px; font-size: 13px;" 
                                onclick="openUpdateModal({{p.id}}, '{{p.name}}', {{p.price}}, {{p.stock}}, '{{p.category}}')">📝 Update</button>
                        
                        <form method="POST" style="margin:0;" onsubmit="return confirm('តើអ្នកពិតជាចង់លុបទំនិញ {{p.name}} នេះមែនទេ?');">
                            <input type="hidden" name="delete_id" value="{{p.id}}">
                            <button type="submit" class="btn btn-danger" style="padding: 6px 12px; font-size: 13px;">🗑️ Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        {% endif %}
        
        {% if active_tab == 'sales' %}
            <div class="sales-container">
                <div class="products-side">
                    <h3 style="color: #007bff; margin-top: 0;">📋 ជ្រើសរើសទំនិញលក់</h3>
                    <table>
                        <tr><th>លេខកូដ (ID)</th><th>ឈ្មោះទំនិញ (Name)</th><th>តម្លៃ (Price)</th><th>ចំនួនស្តុកដែលនៅសល់</th><th>សកម្មភាពលក់</th></tr>
                        {% for p in list_data %}
                        <tr>
                            <td>{{p.id}}</td>
                            <td><strong>{{p.name}}</strong></td>
                            <td style="color:#28a745; font-weight:bold;">${{p.price}}</td>
                            <td>
                                {% if p.stock > 0 %}
                                    <span style="color:#28a745;">{{p.stock}} ដើម/កំប៉ុង</span>
                                {% else %}
                                    <span style="color:#dc3545; font-weight:bold;">អស់ស្តុក</span>
                                {% endif %}
                            </td>
                            <td>
                                <button class="btn btn-info" style="padding: 6px 12px; font-size:13px;" 
                                        onclick="addToCart({{p.id}}, '{{p.name}}', {{p.price}}, {{p.stock}})"
                                        {% if p.stock <= 0 %}disabled style="background:#444; border:none; cursor:not-allowed;"{% endif %}>
                                    🛒 Add to Cart
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>

                <div class="cart-side">
                    <h3 style="color: #ffc107; margin-top: 0;">🛒 កន្ត្រកទំនិញ (Cart)</h3>
                    <table style="margin-top: 10px; font-size: 14px;">
                        <thead>
                            <tr style="background: #1e1e24;">
                                <th>ទំនិញ</th>
                                <th>តម្លៃ</th>
                                <th style="text-align:center; width:90px;">ចំនួន</th>
                                <th>សរុប</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody id="cart-table-body">
                            <tr>
                                <td colspan="5" style="text-align:center; color:#aaa; padding: 20px;">មិនទាន់មានទំនិញក្នុងកន្ត្រក</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div style="margin-top: 20px; display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0;">សរុបរួម:</h3>
                        <h2 style="margin:0; color:#28a745;" id="cart-total-price">$0.00</h2>
                    </div>
                    
                    <button class="btn" style="width:100%; padding: 12px; font-size:16px; margin-top: 15px; background:#28a745;" onclick="submitCheckout()">
                        ✅ Place Order & គិតលុយ
                    </button>
                </div>
            </div>
        {% endif %}

        {% if active_tab == 'history' %}
            <h3 style="color: #007bff; margin-top: 0;">📜 ប្រវត្តិវិក្កយបត្រលក់ចេញ (Sales History)</h3>
            <table>
                <tr><th>លេខរៀងវិក្កយបត្រ (Sale ID)</th><th>ឈ្មោះទំនិញ ​(Products Name)</th><th>ទឹកប្រាក់សរុប (Total Amount)</th><th>កាលបរិច្ឆេទលក់ (Date Time)</th></tr>
                {% for h in list_data %}
                <tr>
                    <td>#000{{h.sale_id}}</td>
                    <td style="color:#28a745; font-weight:bold;">${{h.total}}</td>
                    <td style="color:#aaa;">{{h.date}}</td>
                </tr>
                {% endfor %}
            </table>
        {% endif %}
    </div>

    <div id="updateModal" class="modal">
        <div class="modal-content">
            <h3>📝 កែប្រែព័ត៌មានទំនិញ</h3>
            <form method="POST">
                <input type="hidden" name="update_product" value="1">
                <input type="hidden" name="id" id="update_id">
                
                <label>ឈ្មោះទំនិញ:</label>
                <input type="text" name="name" id="update_name" required>
                
                <label>តម្លៃ ($):</label>
                <input type="number" step="0.01" name="price" id="update_price" required>
                
                <label>ចំនួនក្នុងស្តុក:</label>
                <input type="number" name="stock" id="update_stock" required>
                
                <label>ប្រភេទផលិតផល:</label>
                <select name="category" id="update_category">
                    <option value="None">None</option>
                    <option value="Stationary">Stationary</option>
                    <option value="Electronic">Electronic</option>
                </select>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">បោះបង់</button>
                    <button type="submit" class="btn btn-success">កែប្រែ</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // --- ផ្នែកគ្រប់គ្រង Modal Update ---
        function openUpdateModal(id, name, price, stock, category) {
            document.getElementById('update_id').value = id;
            document.getElementById('update_name').value = name;
            document.getElementById('update_price').value = price;
            document.getElementById('update_stock').value = stock;
            document.getElementById('update_category').value = category;
            document.getElementById('updateModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('updateModal').style.display = 'none';
        }

        window.onclick = function(event) {
            let modal = document.getElementById('updateModal');
            if (event.target == modal) { modal.style.display = 'none'; }
        }

        // --- ផ្នែក Logic របស់កន្ត្រកទំនិញ (Cart Front-end) ---
        let cart = [];

        function addToCart(id, name, price, maxStock) {
            let item = cart.find(p => p.id === id);
            if (item) {
                if (item.qty >= maxStock) {
                    alert(`មិនអាចថែមទៀតបានទេ! ស្តុកទំនិញនេះមានត្រឹមតែ ${maxStock} ប៉ុណ្ណោះ។`);
                    return;
                }
                item.qty += 1;
            } else {
                cart.push({ id: id, name: name, price: price, qty: 1, maxStock: maxStock });
            }
            renderCart();
        }

        function changeQty(id, delta) {
            let item = cart.find(p => p.id === id);
            if (item) {
                item.qty += delta;
                if (item.qty > item.maxStock) {
                    alert(`ស្តុកទំនិញនេះមានត្រឹមតែ ${item.maxStock} ប៉ុណ្ណោះ។`);
                    item.qty = item.maxStock;
                }
                if (item.qty <= 0) {
                    removeFromCart(id);
                    return;
                }
            }
            renderCart();
        }

        function removeFromCart(id) {
            cart = cart.filter(p => p.id !== id);
            renderCart();
        }

        function renderCart() {
            let tbody = document.getElementById('cart-table-body');
            let totalElement = document.getElementById('cart-total-price');
            
            if (cart.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#aaa; padding: 20px;">មិនទាន់មានទំនិញក្នុងកន្ត្រក</td></tr>`;
                totalElement.innerText = "$0.00";
                return;
            }

            tbody.innerHTML = '';
            let totalBill = 0;

            cart.forEach(item => {
                let subtotal = item.price * item.qty;
                totalBill += subtotal;

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${item.name}</strong></td>
                        <td>$${item.price.toFixed(2)}</td>
                        <td style="text-align:center;">
                            <div style="display:flex; justify-content:center; align-items:center; gap:5px;">
                                <button class="btn btn-secondary" style="padding:2px 8px; font-size:12px;" onclick="changeQty(${item.id}, -1)">-</button>
                                <span style="font-weight:bold; min-width:20px;">${item.qty}</span>
                                <button class="btn btn-secondary" style="padding:2px 8px; font-size:12px;" onclick="changeQty(${item.id}, 1)">+</button>
                            </div>
                        </td>
                        <td style="color:#28a745;">$${subtotal.toFixed(2)}</td>
                        <td>
                            <span style="color:#ff6b6b; cursor:pointer; font-weight:bold;" onclick="removeFromCart(${item.id})">❌</span>
                        </td>
                    </tr>
                `;
            });

            totalElement.innerText = `$${totalBill.toFixed(2)}`;
        }

        function submitCheckout() {
            if (cart.length === 0) {
                alert("សូមជ្រើសរើសទំនិញចូលកន្ត្រកជាមុនសិន មុននឹងធ្វើការគិតលុយ!");
                return;
            }

            if (!confirm("តើអ្នកពិតជាចង់បញ្ចប់ការលក់ និងគិតលុយវិក្កយបត្រនេះមែនទេ?")) return;

            // ផ្ញើទិន្នន័យកន្ត្រកទៅកាន់ Backend Python តាមរយៈ Fetch API (JSON)
            fetch('/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cart: cart })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    cart = []; // សម្អាតកន្ត្រកទំនិញលើ Frontend
                    window.location.href = "/history"; // រុញទៅកាន់ទំព័រប្រវត្តិលក់ដើម្បីមើលវិក្កយបត្រ
                } else {
                    alert("កំហុស៖ " + data.message);
                }
            })
            .catch(err => {
                console.error(err);
                alert("មានបញ្ហាក្នុងការតភ្ជាប់ទៅកាន់ម៉ាស៊ីនមេ!");
            });
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)