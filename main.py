"""
DataLens - Web Scraping Browser
Main Entry Point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow


def main():
    """Main entry point for DataLens application"""
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("DataLens")
    app.setOrganizationName("DataLens")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()