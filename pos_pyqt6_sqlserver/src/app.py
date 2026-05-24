import sys
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTabWidget
from auth import LoginDialog
from product_crud import ProductWidget
from sales import SalesWidget
from sales_history import SalesHistoryWidget
from utils import resource_path

class Main_Window(QMainWindow):
    def __init__(self, user):
        super().__init__()
        
        # ១. ទាញយក UI
        try:
            ui_path = resource_path('resources/ui/Main_window.ui')
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading UI: {e}")
            return

        self.user = user

        # ២. កំណត់ StyleSheet ឱ្យ Tab ទាំង ៣ មានពណ៌ស្អាត
        self.apply_tab_styles()

        # ៣. រៀបចំ Tabs និង Widgets ខាងក្នុង
        self.setup_tabs()

        # ៤. បង្ខំឱ្យបង្ហាញ Tab ទី ១ (Products) ជាមុនគេបន្ទាប់ពី Login
        tab_widget = self.findChild(QTabWidget)
        if tab_widget:
            tab_widget.setCurrentIndex(0) # លេខ 0 គឺជា Tab "Products"

        # បង្ហាញព័ត៌មានអ្នកប្រើប្រាស់លើ StatusBar
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Logged in as: {user['username']} ({user['role']})")

    def apply_tab_styles(self):
        """កំណត់ពណ៌ឱ្យ Tab ដូចដែលបានពិភាក្សា"""
        self.setStyleSheet("""
            QTabBar::tab {
                background-color: #333333;
                color: #ffffff;
                min-width: 120px;
                padding: 10px;
                font-size: 14px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50; /* ពណ៌បៃតងពេលចុចលើវា */
                font-weight: bold;
                border-bottom: 2px solid white;
            }
            QTabBar::tab:hover {
                background-color: #555555;
            }
        """)

    def setup_tabs(self):
        """មុខងាររៀបចំ Layout ឱ្យ Widget ខាងក្នុងរីកពេញ Tab នីមួយៗ"""
        try:
            # បង្កើត Instance របស់ Widget នីមួយៗ
            self.products_widget = ProductWidget()
            self.sales_widget = SalesWidget()
            self.history_widget = SalesHistoryWidget()

            # ផ្គូផ្គង Tab ពី Designer ជាមួយ Widget ក្នុងកូដ
            # ត្រូវប្រាកដថា self.tabProducts លេខរៀងត្រូវតាម Designer
            tabs_mapping = {
                self.tabProducts: self.products_widget,
                self.tabSales: self.sales_widget,
                self.tabHistory: self.history_widget
            }

            for tab, widget in tabs_mapping.items():
                # បង្កើត Layout ប្រសិនបើមិនទាន់មាន ដើម្បីឱ្យ Widget រីកពេញ Tab
                if tab.layout() is None:
                    layout = QVBoxLayout(tab)
                    layout.setContentsMargins(5, 5, 5, 5) 
                    layout.setSpacing(0)
                    tab.setLayout(layout)
                
                # បន្ថែម Widget ទៅក្នុង Layout
                tab.layout().addWidget(widget)
                
        except AttributeError as e:
            print(f"AttributeError: {e}. សូមពិនិត្យឈ្មោះ objectName ក្នុង Qt Designer ឡើងវិញ!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # កំណត់ Icon ឱ្យកម្មវិធី
    app.setWindowIcon(QIcon(resource_path('icon/cashier.png')))
    
    # បើកផ្ទាំង Login
    login = LoginDialog()
    
    # ប្រសិនបើ Login ជោគជ័យ (exec == 1)
    if login.exec() == 1 and login.user:
        window = Main_Window(login.user)
        window.showMaximized() # បង្ហាញពេញអេក្រង់
        sys.exit(app.exec())
    else:
        sys.exit(0)