import sys
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from database import get_connection
from utils import resource_path 

class SalesHistoryWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ១. ការកំណត់ Path ឱ្យត្រូវចំទីតាំង
        try:
            # ផ្ទៀងផ្ទាត់ឈ្មោះ File UI ឱ្យត្រូវ (Sales_history.ui ឬ SalesHistory.ui)
            ui_file = resource_path('resources/ui/SalesHistory.ui')

            if not os.path.exists(ui_file):
                base_path = os.path.dirname(os.path.abspath(__file__))
                ui_file = os.path.join(base_path, "resources", "ui", "SalesHistory.ui")

            if not os.path.exists(ui_file):
                raise FileNotFoundError(f"រកមិនឃើញ File UI ទេ: {ui_file}")

            uic.loadUi(ui_file, self)
            
        except Exception as e:
            print(f"Critical Error: មិនអាច Load UI បានទេ។ {e}")
            return

        # ២. ការតភ្ជាប់ប៊ូតុង និង Table
        self.initialize_ui_logic()

    def initialize_ui_logic(self):
        try:
            # កែឈ្មោះឱ្យត្រូវតាមរូបភាព image_15b868.png
            # ប៊ូតុងឈ្មោះ btnResfresh និង តារាងឈ្មោះ tblSalesHistory
            if hasattr(self, 'btnResfresh') and hasattr(self, 'tblSalesHistory'):
                self.btnResfresh.clicked.connect(self.load_sales)
                
                # រៀបចំ Column Table
                self.tblSalesHistory.setColumnCount(3)
                self.tblSalesHistory.setHorizontalHeaderLabels(['លេខវិក្កយបត្រ', 'សរុប ($)', 'កាលបរិច្ឆេទ'])
                
                # ទាញទិន្នន័យមកបង្ហាញភ្លាមៗ
                self.load_sales()
            else:
                missing = []
                if not hasattr(self, 'btnResfresh'): missing.append("btnResfresh")
                if not hasattr(self, 'tblSalesHistory'): missing.append("tblSalesHistory")
                print(f"UI Warning: បាត់ Object {', '.join(missing)} ក្នុង Qt Designer")
                
        except AttributeError as e:
            print(f"UI Logic Error: {e}")

    def load_sales(self):
        """ទាញទិន្នន័យពី SQL Server មកបង្ហាញក្នុង Table"""
        try:
            with get_connection() as conn:
                if conn is None:
                    raise Exception("ការតភ្ជាប់ Database បរាជ័យ")
                    
                cur = conn.cursor()
                # ទាញទិន្នន័យពីតារាង Sales
                query = 'SELECT sale_id, total_amount, sale_date FROM DB_shop.dbo.Sales ORDER BY sale_id DESC'
                cur.execute(query)
                rows = cur.fetchall()
            
            # សម្អាតទិន្នន័យចាស់ រួចបញ្ចូលថ្មី
            self.tblSalesHistory.setRowCount(0)
            for r, row in enumerate(rows):
                self.tblSalesHistory.insertRow(r)
                
                # ១. លេខវិក្កយបត្រ (Sale ID)
                self.tblSalesHistory.setItem(r, 0, QTableWidgetItem(str(row[0])))
                
                # ២. សរុប ($)
                amount = f"$ {float(row[1]):.2f}" if row[1] is not None else "$ 0.00"
                self.tblSalesHistory.setItem(r, 1, QTableWidgetItem(amount))
                
                # ៣. កាលបរិច្ឆេទ (Format ឱ្យខ្លីងាយមើល)
                date_str = row[2].strftime("%Y-%m-%d %H:%M") if row[2] else "N/A"
                self.tblSalesHistory.setItem(r, 2, QTableWidgetItem(date_str))
                
        except Exception as e:
            print(f"Database Error: {e}")
            QMessageBox.warning(self, "Database Error", f"មានបញ្ហាក្នុងការទាញទិន្នន័យ: {e}")

    def showEvent(self, event):
        """រាល់ពេលចុចប្តូរ Tab មកកាន់ Sales History ឱ្យវាទាញទិន្នន័យថ្មីភ្លាម"""
        super().showEvent(event)
        if hasattr(self, 'tblSalesHistory'):
            self.load_sales()