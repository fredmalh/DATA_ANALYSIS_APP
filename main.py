"""
Data Analysis Application - Main Entry Point
A modern GUI application for data analysis with file upload and interactive visualization.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow


def main():
    """Initialize and display the main application window."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Data Analysis Application")
    app.setOrganizationName("Data Analysis")
    
    # Apply dark theme stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #212121;
        }
        QWidget {
            background-color: #212121;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #0d47a1;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            min-height: 32px;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:pressed {
            background-color: #0a3d91;
        }
        QPushButton:disabled {
            background-color: #303030;
            color: #757575;
        }
        QLabel {
            color: #FFFFFF;
        }
        QTableWidget {
            background-color: #303030;
            color: #FFFFFF;
            border: 1px solid #424242;
            gridline-color: #424242;
        }
        QHeaderView::section {
            background-color: #424242;
            color: #FFFFFF;
            padding: 8px;
            border: none;
        }
        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: #303030;
            width: 12px;
            height: 12px;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background-color: #616161;
            min-height: 20px;
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background-color: #757575;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    window.setWindowTitle("Data Analysis Application")
    window.resize(1200, 800)
    window.setMinimumSize(800, 600)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
