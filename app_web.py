from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'pos_secret_key_123'

# ទិន្នន័យគំរូសម្រាប់សាកល្បង Login
USER_DATA = {
    "admin": "1234"
}

# ទិន្នន័យគំរូបញ្ជីផលិតផល
def get_products():
    return [
        (1, "កូកាកូឡា", "0.50", 120),
        (2, "ទឹកបរិសុទ្ធ", "0.25", 200),
        (3, "នំប៉័ង", "1.00", 50)
    ]

# ១. ផ្ទាំង LOGIN (បង្ហាញមុនគេបង្អស់)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USER_DATA and USER_DATA[username] == password:
            return redirect(url_for('dashboard'))
        else:
            flash("ឈ្មោះអ្នកប្រើប្រាស់ ឬ លេខសម្ងាត់មិនត្រឹមត្រូវឡើយ!", "error")
            
    login_template = """
    <html>
    <head>
        <title>POS System - Login</title>
        <style>
            body { font-family: 'Khmer OS Battambang', 'Segoe UI', sans-serif; background-color: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 320px; }
            h2 { text-align: center; color: #333; margin-bottom: 25px; font-size: 22px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #666; font-size: 14px; }
            input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background-color: #007bff; border: none; color: white; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 10px; }
            button:hover { background-color: #0056b3; }
            .error-msg { color: red; font-size: 14px; text-align: center; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🔐 ប្រព័ន្ធ POS - ឡូហ្គីន</h2>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, message in messages %}
                  <div class="error-msg">{{ message }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}

            <form method="POST">
                <div class="form-group">
                    <label>ឈ្មោះអ្នកប្រើប្រាស់ (Username):</label>
                    <input type="text" name="username" placeholder="admin" required>
                </div>
                <div class="form-group">
                    <label>លេខសម្ងាត់ (Password):</label>
                    <input type="password" name="password" placeholder="1234" required>
                </div>
                <button type="submit">ចូលប្រើប្រាស់</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_template)

# ២. ផ្ទាំង DASHBOARD (បង្ហាញក្រោយពេល Login ត្រូវ)
@app.route('/dashboard')
def dashboard():
    products = get_products()
    dashboard_template = """
    <html>
    <head>
        <title>POS - បញ្ជីផលិតផល</title>
        <style>
            body { font-family: 'Khmer OS Battambang', 'Segoe UI', sans-serif; padding: 30px; background-color: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #28a745; color: white; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .btn-logout { padding: 8px 15px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }
            .btn-logout:hover { background-color: #bd2130; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📦 បញ្ជីផលិតផលក្នុងប្រព័ន្ធ (Flask Web)</h2>
                <a href="{{ url_for('login') }}" class="btn-logout">ចាកចេញ</a>
            </div>
            <table>
                <tr>
                    <th>លេខកូដ</th><th>ឈ្មោះផលិតផល</th><th>តម្លៃ ($)</th><th>ចំនួនក្នុងស្តុក</th>
                </tr>
                {% for row in products %}
                <tr>
                    <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(dashboard_template, products=products)

if __name__ == '__main__':
    app.run(debug=True)