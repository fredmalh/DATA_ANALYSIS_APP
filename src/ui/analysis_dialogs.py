"""
Analysis Dialogs Module
Dialog windows for displaying analysis results.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any, Optional


class BaseAnalysisDialog(QDialog):
    """Base class for analysis result dialogs."""
    
    def __init__(self, title: str, result_data: Dict[str, Any], parent=None):
        """
        Initialize the analysis dialog.
        
        Args:
            title: Dialog window title
            result_data: Dictionary containing analysis results
            parent: Parent window
        """
        super().__init__(parent)
        self.result_data = result_data
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Set window flags to enable minimize and maximize buttons
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Make dialog non-modal so main window remains accessible
        self.setModal(False)
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #212121;
            }
            QLabel {
                color: #FFFFFF;
            }
            QTextEdit {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
            }
        """)
        
        self._init_ui()
    
    def _init_ui(self):
        """Build and display the dialog UI. Override in subclasses for custom layouts."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(self.windowTitle())
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Summary (if available)
        if 'summary' in self.result_data and self.result_data['summary']:
            summary_text = QLabel(self.result_data['summary'])
            summary_text.setStyleSheet("color: #BDBDBD; font-size: 12px; padding-bottom: 10px;")
            summary_text.setWordWrap(True)
            layout.addWidget(summary_text)
        
        # Content area (to be populated by subclasses or _build_content)
        self.content_widget = self._build_content()
        if self.content_widget:
            layout.addWidget(self.content_widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
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
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
    
    def _build_content(self) -> Optional[QWidget]:
        """
        Build the main content area. Override in subclasses.
        
        Returns:
            QWidget containing the result display, or None if using default
        """
        # Default: show error message if analysis failed
        if not self.result_data.get('success', False):
            error_label = QLabel(f"Error: {self.result_data.get('error', 'Unknown error')}")
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setWordWrap(True)
            return error_label
        
        return None


class StatisticsResultDialog(BaseAnalysisDialog):
    """Dialog for displaying statistical analysis results."""
    
    def _build_content(self) -> Optional[QWidget]:
        """Build content for statistics results."""
        if not self.result_data.get('success', False):
            return super()._build_content()
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #424242;
                border-radius: 5px;
                background-color: #212121;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        content_widget.setLayout(content_layout)
        
        # Get statistics data
        stats_data = self.result_data.get('data', {})
        
        # Create table for statistics
        if stats_data:
            table = self._create_statistics_table(stats_data)
            content_layout.addWidget(table)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    def _create_statistics_table(self, stats_data: Dict[str, Any]) -> QTableWidget:
        """Create a table widget displaying statistics."""
        table = QTableWidget()
        
        # Determine number of rows and columns
        # Assuming stats_data is a dict like {'column_name': {'mean': 1.5, 'std': 0.3, ...}}
        if isinstance(stats_data, dict) and stats_data:
            # Get all unique statistic names
            stat_names = set()
            for col_stats in stats_data.values():
                if isinstance(col_stats, dict):
                    stat_names.update(col_stats.keys())
            
            stat_names = sorted(stat_names)
            columns = list(stats_data.keys())
            
            # Set table dimensions
            table.setRowCount(len(stat_names))
            table.setColumnCount(len(columns))
            
            # Set headers
            table.setHorizontalHeaderLabels(columns)
            table.setVerticalHeaderLabels(stat_names)
            
            # Populate data
            for col_idx, col_name in enumerate(columns):
                col_stats = stats_data.get(col_name, {})
                for row_idx, stat_name in enumerate(stat_names):
                    value = col_stats.get(stat_name, 'N/A')
                    item = QTableWidgetItem(str(value) if value != 'N/A' else 'N/A')
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        
        # Resize columns to content
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
        return table


class TextResultDialog(BaseAnalysisDialog):
    """Dialog for displaying text-based analysis results."""
    
    def _build_content(self) -> Optional[QWidget]:
        """Build content for text results."""
        if not self.result_data.get('success', False):
            return super()._build_content()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Get text data
        text_data = self.result_data.get('data', '')
        if isinstance(text_data, str):
            text_edit.setPlainText(text_data)
        else:
            text_edit.setPlainText(str(text_data))
        
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        return text_edit

