from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from database import get_connection
from utils import resource_path

class SalesWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi(resource_path('resources/ui/Sales.ui'), self)
        except Exception as e:
            print(f"Error loading Sales UI: {e}")

        # --- ចំណុចបន្ថែម៖ កំណត់ឱ្យវាយចំនួនបានច្រើន ---
        if hasattr(self, 'spnQty'):
            self.spnQty.setMaximum(10000) # កំណត់ឱ្យទិញបានដល់ ១ ម៉ឺនមុខ
        # -------------------------------------------

        # Connect Buttons
        self.btnAddToCart.clicked.connect(self.add_to_cart)
        self.btnCheckout.clicked.connect(self.checkout)
        self.btnClearCart.clicked.connect(self.clear_cart)
        
        self.tblCart.setColumnCount(5)
        self.tblCart.setHorizontalHeaderLabels(['ProductID','Name','Qty','Price','Subtotal'])
        self.cart = []
        self.load_products_combo()
        self.update_total()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_products_combo()

    def load_products_combo(self):
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                query = 'SELECT product_id, product_name, price, stock_quantity FROM DB_shop.dbo.Table_Product WHERE stock_quantity > 0 ORDER BY product_name'
                cur.execute(query)
                self.products = cur.fetchall()
            
            self.cmbProducts.clear() 
            for p in self.products:
                self.cmbProducts.addItem(f"{p[1]} ($ {p[2]:.2f}) [Stock {p[3]}]", p[0])
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"Load Combo Error: {str(e)}")

    def add_to_cart(self):
        idx = self.cmbProducts.currentIndex()
        if idx < 0:
            return
            
        pid = self.cmbProducts.currentData()
        name = self.products[idx][1]
        price = float(self.products[idx][2])
        stock_available = int(self.products[idx][3])
        qty = int(self.spnQty.value())
        
        if qty <= 0:
            QMessageBox.warning(self, 'Qty', 'Quantity must be > 0')
            return
            
        if qty > stock_available:
            QMessageBox.warning(self, 'Stock', f'Not enough stock. Available: {stock_available}')
            return

        subtotal = price * qty
        self.cart.append({'product_id': pid, 'name': name, 'qty': qty, 'price': price, 'subtotal': subtotal})
        self.refresh_cart_table()
        self.update_total()

    def refresh_cart_table(self):
        self.tblCart.setRowCount(len(self.cart))
        for r, item in enumerate(self.cart):
            self.tblCart.setItem(r, 0, QTableWidgetItem(str(item['product_id'])))
            self.tblCart.setItem(r, 1, QTableWidgetItem(item['name']))
            self.tblCart.setItem(r, 2, QTableWidgetItem(str(item['qty'])))
            self.tblCart.setItem(r, 3, QTableWidgetItem(f"{item['price']:.2f}"))
            self.tblCart.setItem(r, 4, QTableWidgetItem(f"{item['subtotal']:.2f}"))

    def update_total(self):
        total = sum(i['subtotal'] for i in self.cart)
        if hasattr(self, 'lblTotal'):
            self.lblTotal.setText(f"$ {total:.2f}")

    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart_table()
        self.update_total()

    def checkout(self):
        """ដោះស្រាយបញ្ហា Checkout Error (payment_method NULL)"""
        if not self.cart:
            QMessageBox.information(self, 'Checkout', 'Cart is empty')
            return
            
        try:
            total = sum(i['subtotal'] for i in self.cart)
            with get_connection() as conn:
                cur = conn.cursor()
                
                # បន្ថែម 'payment_method' ទៅក្នុង Query និងដាក់តម្លៃជា 'Cash'
                # នេះនឹងជួយឱ្យអ្នកលែងជាប់ Error ដូចក្នុងរូបភាពទៀតហើយ
                query_sale = '''INSERT INTO DB_shop.dbo.Sales 
                                (total_amount, payment_method, sale_date) 
                                OUTPUT INSERTED.sale_id 
                                VALUES (?, 'Cash', GETDATE())'''
                
                cur.execute(query_sale, (total,))
                sale_id = cur.fetchone()[0]
                
                for it in self.cart:
                    # បញ្ចូលទំនិញទៅក្នុង SaleItems
                    cur.execute('''INSERT INTO DB_shop.dbo.SaleItems 
                                   (sale_id, product_id, qty, price) 
                                   VALUES (?, ?, ?, ?)''',
                                (sale_id, it['product_id'], it['qty'], it['price']))
                    
                    # កាត់ស្តុកចេញពី Table_Product
                    cur.execute('''UPDATE DB_shop.dbo.Table_Product 
                                   SET stock_quantity = stock_quantity - ? 
                                   WHERE product_id = ?''', 
                                (it['qty'], it['product_id']))
                
                conn.commit()
                
            self.clear_cart()
            self.load_products_combo() # បច្ចុប្បន្នភាពចំនួនស្តុកក្នុងបញ្ជីរើសទំនិញ
            QMessageBox.information(self, 'Success', 'Sale recorded and stock updated!')
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"Checkout Error: {str(e)}")