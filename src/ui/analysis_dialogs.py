"""
Analysis Dialogs Module
Pop-up windows for displaying analysis results (text, tables, graphs).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pandas as pd


class AnalysisDialog:
    """Base class for analysis result dialogs."""
    
    @staticmethod
    def show_text_dialog(parent, title: str, content: str):
        """Display a text result in a dialog."""
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(content)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
            }
        """)
        layout.addWidget(text_edit)
        
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        close_button.setStyleSheet("""
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
        """)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    @staticmethod
    def show_table_dialog(parent, title: str, data: pd.DataFrame):
        """Display a table result in a dialog."""
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.resize(800, 500)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(len(data.columns))
        table.setRowCount(min(50, len(data)))  # Limit to 50 rows
        
        # Set headers
        table.setHorizontalHeaderLabels([str(col) for col in data.columns])
        
        # Populate data
        for row_idx, (idx, row) in enumerate(data.head(50).iterrows()):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val) if pd.notna(val) else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)
        
        # Style the table
        table.setStyleSheet("""
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
                font-weight: bold;
            }
        """)
        
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(table)
        
        # Info label
        if len(data) > 50:
            info_label = QLabel(f"Showing first 50 of {len(data)} rows")
            info_label.setStyleSheet("color: #757575; font-size: 12px;")
            layout.addWidget(info_label)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        close_button.setStyleSheet("""
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
        """)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    @staticmethod
    def show_graph_dialog(parent, title: str, graph_html: str):
        """Display a graph result in a dialog using Plotly."""
        # For Plotly graphs, we'll use QTextEdit with HTML support
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Use QTextEdit to display HTML (Plotly graphs)
        html_view = QTextEdit()
        html_view.setHtml(graph_html)
        html_view.setReadOnly(True)
        html_view.setStyleSheet("""
            QTextEdit {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
            }
        """)
        layout.addWidget(html_view)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        close_button.setStyleSheet("""
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
        """)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
