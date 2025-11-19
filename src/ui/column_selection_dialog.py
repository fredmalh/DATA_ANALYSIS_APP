"""
Column Selection Dialog Module
Dialog for selecting columns to drop from the dataset.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import List


class ColumnSelectionDialog(QDialog):
    """Dialog for selecting columns to drop from the dataset."""
    
    def __init__(self, column_names: List[str], parent=None):
        """
        Initialize the column selection dialog.
        
        Args:
            column_names: List of column names to display
            parent: Parent window
        """
        super().__init__(parent)
        self.column_names = column_names
        self.selected_columns = []
        self.checkboxes = {}
        
        self.setWindowTitle("Select Columns to Drop")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        
        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #212121;
            }
            QLabel {
                color: #FFFFFF;
            }
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #64B5F6;
                border-radius: 3px;
                background-color: #303030;
            }
            QCheckBox::indicator:checked {
                background-color: #0d47a1;
                border-color: #0d47a1;
            }
            QCheckBox::indicator:hover {
                border-color: #1565c0;
            }
        """)
        
        self._init_ui()
    
    def _init_ui(self):
        """Build and display the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Select Columns to Drop")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Info text
        info_text = QLabel(
            f"Select the columns you want to drop from the dataset.\n"
            f"Total columns: {len(self.column_names)}"
        )
        info_text.setStyleSheet("color: #BDBDBD; font-size: 12px; padding-bottom: 10px;")
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
        
        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #424242;
                border-radius: 5px;
                background-color: #212121;
            }
        """)
        
        # Container for checkboxes
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setSpacing(8)
        checkbox_layout.setContentsMargins(15, 15, 15, 15)
        checkbox_widget.setLayout(checkbox_layout)
        
        # Create checkboxes for each column
        for col_name in self.column_names:
            checkbox = QCheckBox(str(col_name))
            checkbox.setStyleSheet("padding: 5px;")
            self.checkboxes[col_name] = checkbox
            checkbox_layout.addWidget(checkbox)
        
        # Add stretch at the end
        checkbox_layout.addStretch()
        
        checkbox_widget.setLayout(checkbox_layout)
        scroll_area.setWidget(checkbox_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Select All button
        select_all_button = QPushButton("Select All")
        select_all_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        select_all_button.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_button)
        
        # Deselect All button
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        deselect_all_button.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #616161;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Drop button
        drop_button = QPushButton("Drop Selected")
        drop_button.setStyleSheet("""
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
        drop_button.clicked.connect(self._on_drop_clicked)
        button_layout.addWidget(drop_button)
        
        layout.addLayout(button_layout)
    
    def _select_all(self):
        """Select all checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def _deselect_all(self):
        """Deselect all checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def _on_drop_clicked(self):
        """Handle drop button click - validate and accept."""
        # Get selected columns
        self.selected_columns = [
            col_name for col_name, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        ]
        
        # Validation
        if not self.selected_columns:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("No Columns Selected")
            msg_box.setText("Please select at least one column to drop.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            return
        
        # Warn if trying to drop all columns
        if len(self.selected_columns) == len(self.column_names):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("You are about to drop all columns from the dataset.")
            msg_box.setInformativeText("This will result in an empty dataset. Are you sure?")
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            if msg_box.exec() == QMessageBox.StandardButton.No:
                return
        
        # Accept dialog
        self.accept()
    
    def get_selected_columns(self) -> List[str]:
        """
        Get the list of selected column names.
        
        Returns:
            List of column names to drop
        """
        return self.selected_columns

