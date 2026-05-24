from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

# កូដភ្ជាប់ទៅកាន់ Database (កែតម្រូវទៅតាម Database របស់អ្នក)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pos_pyqt6_sqlserver"
    )

@app.route('/')
def index():
    # ទាញយកទិន្នន័យផលិតផលមកបង្ហាញលើ Web
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)