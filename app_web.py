from flask import Flask, render_template_string
import pyodbc # ឬបណ្ណាល័យដែលអ្នកប្រើភ្ជាប់ទៅ SQL Server

app = Flask(__name__)

def get_products():
    # កូដភ្ជាប់ទៅ SQL Server របស់អ្នក (ដូចក្នុង database.py)
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...')
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, price, stock_quantity FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    products = get_products()
    
    # បង្កើតផ្ទៃតារាង HTML ងាយៗដើម្បីបង្ហាញលើ Web Browser
    html_template = """
    <html>
    <head><title>POS Product List</title></head>
    <body>
        <h2>បញ្ជីផលិតផលពីប្រព័ន្ធ POS</h2>
        <table border="1">
            <tr>
                <th>លេខកូដ</th><th>ឈ្មោះផលិតផល</th><th>តម្លៃ</th><th>ចំនួនក្នុងស្តុក</th>
            </tr>
            {% for row in products %}
            <tr>
                <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, products=products)

if __name__ == '__main__':
    app.run(debug=True)