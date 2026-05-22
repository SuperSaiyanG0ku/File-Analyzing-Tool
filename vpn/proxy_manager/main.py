import sys
import os

# Add the current directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.proxy_handler import ProxyHandler

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Proxy Manager")
    app.setApplicationDisplayName("Proxy Manager Pro")
    
    # Set application-wide font
    # font = QFont("Segoe UI", 10)
    # app.setFont(font)
    
    # Initialize Core Proxy Handler (Handles DB and Windows Registry)
    handler = ProxyHandler()
    
    # Initialize Main Window
    window = MainWindow(handler)
    window.show()
    
    # Execute the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
