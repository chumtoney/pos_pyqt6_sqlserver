from flask import Flask, render_template_string

app = Flask(__name__)

# បង្កើតទិន្នន័យសាកល្បងធម្មតា (មិនទាន់ភ្ជាប់ទៅ Database ខាងក្រៅ)
def get_products():
    return [
        (1, "កូកាកូឡា", "0.50", 120),
        (2, "ទឹកបរិសុទ្ធ", "0.25", 200),
        (3, "នំប៉័ង", "1.00", 50)
    ]

@app.route('/')
def index():
    products = get_products()
    
    html_template = """
    <html>
    <head>
        <title>POS Product List</title>
        <style>
            body { font-family: 'Khmer OS Battambang', sans-serif; padding: 20px; }
            table { width: 50%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>📦 បញ្ជីផលិតផលពីប្រព័ន្ធ POS (Flask Web)</h2>
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
    </body>
    </html>
    """
    return render_template_string(html_template, products=products)

if __name__ == '__main__':
    app.run(debug=True)