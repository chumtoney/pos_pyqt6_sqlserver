import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server')
    server = os.getenv('DB_SERVER', 'localhost')
    database = os.getenv('DB_DATABASE', 'DB_shop')
    username = os.getenv('DB_USERNAME', '').strip()
    password = os.getenv('DB_PASSWORD', '').strip()
    trusted = os.getenv('DB_TRUSTED_CONNECTION', 'yes').lower() in ['1','true','yes']

    encrypt = os.getenv('DB_ENCRYPT', 'yes')
    trust_cert = os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'yes')

    if trusted or (not username and not password):
        conn_str = (
            "Driver={ODBC Driver 18 for SQL Server};"
            "Server=DESKTOP-D1D1PGG\SQLEXPRESS;" # ឈ្មោះ Server របស់អ្នក
            "Database=DB_shop;"  # <--- ត្រូវប្រាកដថាឈ្មោះនេះត្រឹមត្រូវតាមក្នុង SSMS
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
        conn_str = (
            f'DRIVER={{{driver}}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            f'Encrypt={encrypt};'
            f'TrustServerCertificate={trust_cert};'
        )

    return pyodbc.connect(conn_str)