import sys
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout
from utils import resource_path
from product_crud import ProductWidget # Import widget ដែលយើងបានកែពីមុន

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            # ផ្លូវទៅកាន់ file UI
            ui_file = resource_path('resources/ui/Main_window.ui')
            uic.loadUi(ui_file, self)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"មិនអាចរកឃើញឯកសារ UI ទេ: {str(e)}")
            sys.exit(1)

        self.setWindowTitle("POS System - SQL Server")

        # --- ការតភ្ជាប់ប៊ូតុងទៅកាន់ផ្នែកផ្សេងៗ ---
        
        # ប្រសិនបើអ្នកមានប៊ូតុងសម្រាប់បើក Product Management
        if hasattr(self, 'btnManageProducts'):
            self.btnManageProducts.clicked.connect(self.show_products)

    def show_products(self):
        # បង្កើត Object នៃ ProductWidget
        self.product_window = ProductWidget()
        
        # ប្រសិនបើអ្នកចង់បើកវាជា Window ថ្មីដាច់ដោយឡែក
        self.product_window.show()
        
        # ឬប្រសិនបើអ្នកចង់ដាក់វាចូលក្នុង QStackedWidget ឬ Frame ណាមួយក្នុង MainWindow:
        # self.mainContainer.addWidget(self.product_window)
        # self.mainContainer.setCurrentWidget(self.product_window)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()