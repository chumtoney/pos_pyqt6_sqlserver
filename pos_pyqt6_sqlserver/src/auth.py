from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox
from database import get_connection
from utils import resource_path

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path('resources/ui/login.ui'), self)
        self.btnLogin.clicked.connect(self.handle_login)
        self.user = None

    def handle_login(self):
        u = self.txtUsername.text().strip()
        p = self.txtPassword.text().strip()
        
        if not u or not p:
            QMessageBox.warning(self, 'Login', 'Enter username and password')
            return
            
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                # កែឈ្មោះ Table ទៅជា Table_User 
                # កែឈ្មោះ Column ទៅជា password_hash, role_id, status តាម SQL របស់អ្នក
                query = """
                    SELECT user_id, username, role_id, status 
                    FROM DB_shop.dbo.Table_User 
                    WHERE username=? AND password_hash=?
                """
                cur.execute(query, (u, p))
                row = cur.fetchone()
                
                # បញ្ជាក់៖ ក្នុង DB របស់អ្នក Column status ប្រហែលជាប្រើពាក្យ 'Active' (NVARCHAR) 
                # មិនមែនលេខ 1 (BIT) ទេ។ ខ្ញុំប្រើលក្ខខណ្ឌឆែកអក្សរ 'Active'
                if row:
                    # ពិនិត្យស្ថានភាព User ( status == 'Active' )
                    if row[3] == 'Active' or row[3] == 1: 
                        self.user = {
                            'id': row[0], 
                            'username': row[1], 
                            'role': row[2]
                        }
                        self.accept()
                    else:
                        QMessageBox.warning(self, 'Login', 'Your account is inactive!')
                else:
                    QMessageBox.critical(self, 'Login', 'Invalid username or password')
                    
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"Error: {str(e)}")