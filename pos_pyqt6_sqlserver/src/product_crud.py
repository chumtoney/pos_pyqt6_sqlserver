from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from database import get_connection
from utils import resource_path

class ProductWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            ui_path = resource_path('resources/ui/Products.ui')
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading UI: {e}")

        # --- ចំណុចបន្ថែម៖ កំណត់ឱ្យវាយលេខបានច្រើនខ្ទង់ ---
        # កំណត់តម្លៃអតិបរមា (Maximum) ឱ្យ spnPrice និង spnStock
        if hasattr(self, 'spnPrice'):
            self.spnPrice.setMaximum(9999999.99) # ដាក់បានដល់ ៧ ខ្ទង់
        if hasattr(self, 'spnStock'):
            self.spnStock.setMaximum(1000000)    # ដាក់បានដល់ ១ លាន
        # -------------------------------------------

        # ការតភ្ជាប់ប៊ូតុង (Signals & Slots)
        self.btnAddProducts.clicked.connect(self.add_product)
        self.btnEditProducts.clicked.connect(self.edit_product)
        self.btnDeleteProducts.clicked.connect(self.delete_product)
        self.btnRefreshProducts.clicked.connect(self.load_products)
        
        # កំណត់ចំនួនជួរឈរសម្រាប់ Table
        self.tabProducts.setColumnCount(4)
        self.tabProducts.setHorizontalHeaderLabels(['ID', 'Name', 'Price', 'Stock'])
        
        # ភ្ជាប់ Signal នៅពេលអ្នកប្រើចុចលើជួរណាមួយក្នុងតារាង
        self.tabProducts.itemSelectionChanged.connect(self.on_products_selected)
        
        # ទាញទិន្នន័យមកបង្ហាញដំបូង
        self.load_products()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_products()
        
    def load_products(self):
        """ទាញទិន្នន័យពី SQL Server មកបង្ហាញក្នុង QTableWidget"""
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                query = 'SELECT product_id, product_name, price, stock_quantity FROM DB_shop.dbo.Table_Product ORDER BY product_id DESC'
                cur.execute(query)
                rows = cur.fetchall()
                
            self.tabProducts.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    if c == 0: # មិនអនុញ្ញាតឱ្យកែលេខ ID ក្នុងតារាងផ្ទាល់
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabProducts.setItem(r, c, item)
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"Load Error: {str(e)}")

    def on_products_selected(self):
        """នៅពេលចុចលើជួរក្នុងតារាង វានឹងទាញទិន្នន័យមកដាក់ក្នុង TextBox/Spinner"""
        row = self.tabProducts.currentRow()
        if row >= 0:
            try:
                name = self.tabProducts.item(row, 1).text()
                price = float(self.tabProducts.item(row, 2).text())
                stock = int(self.tabProducts.item(row, 3).text())
                
                # បង្ហាញក្នុង UI
                self.txtName.setText(name)
                self.spnPrice.setValue(price)
                self.spnStock.setValue(stock)
            except:
                pass

    def add_product(self):
        """បន្ថែមផលិតផលថ្មី និងដោះស្រាយ Error category_id/barcode"""
        name = self.txtName.text().strip()
        price = float(self.spnPrice.value())
        stock = int(self.spnStock.value())
        
        if not name:
            QMessageBox.warning(self, 'Validation', 'Product name is required')
            return
            
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                # Query ដែលមានទាំង category_id និង barcode ដើម្បីជៀសវាង Error NULL
                query = '''INSERT INTO DB_shop.dbo.Table_Product 
                           (product_name, price, stock_quantity, category_id, barcode) 
                           VALUES (?, ?, ?, 1, '000000')''' 
                
                cur.execute(query, (name, price, stock))
                conn.commit()
                
            self.txtName.clear()
            self.spnPrice.setValue(0.0)
            self.spnStock.setValue(0)
            self.load_products()
            QMessageBox.information(self, 'Success', 'Product added successfully')
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"Add Error: {str(e)}")
            
    def _selected_product_id(self):
        """ទាញយក ID នៃផលិតផលដែលបានជ្រើសរើសក្នុងតារាង"""
        row = self.tabProducts.currentRow()
        if row < 0 or self.tabProducts.item(row, 0) is None:
            return None
        return int(self.tabProducts.item(row, 0).text())

    def edit_product(self):
        """កែប្រែផលិតផល"""
        pid = self._selected_product_id()
        if not pid:
            QMessageBox.information(self, 'Edit', 'Please select a product from the table first')
            return
            
        name = self.txtName.text().strip()
        price = float(self.spnPrice.value())
        stock = int(self.spnStock.value())
        
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                query = 'UPDATE DB_shop.dbo.Table_Product SET product_name=?, price=?, stock_quantity=? WHERE product_id=?'
                cur.execute(query, (name, price, stock, pid))
                conn.commit()
            self.load_products()
            QMessageBox.information(self, 'Success', 'Product updated successfully')
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"Update Error: {str(e)}")

    def delete_product(self):
        """លុបផលិតផល"""
        pid = self._selected_product_id()
        if not pid:
            QMessageBox.information(self, 'Delete', 'Please select a product to delete')
            return
            
        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to delete this product?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_connection() as conn:
                    cur = conn.cursor()
                    query = 'DELETE FROM DB_shop.dbo.Table_Product WHERE product_id=?'
                    cur.execute(query, (pid,))
                    conn.commit()
                self.load_products()
                QMessageBox.information(self, 'Success', 'Product deleted successfully')
            except Exception as e:
                QMessageBox.critical(self, 'DB Error', f"Delete Error: {str(e)}")