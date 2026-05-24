import os
import sys

def resource_path(relative_path):
    try:
        # សម្រាប់ពេល compile ជា .exe (PyInstaller)
        base_path = sys._MEIPASS
    except Exception:
        # សម្រាប់ពេល run script ធម្មតា
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)