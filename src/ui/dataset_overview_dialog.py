"""
Dataset Overview Dialog Module
Dialog for displaying dataset overview information.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any
from src.ui.analysis_dialogs import BaseAnalysisDialog


class DatasetOverviewDialog(BaseAnalysisDialog):
    """Dialog for displaying dataset overview results."""
    
    def _build_content(self) -> QWidget:
        """Build content for dataset overview results."""
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
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_widget.setLayout(content_layout)
        
        data = self.result_data.get('data', {})
        
        # Dimensions section
        dimensions = data.get('dimensions', {})
        if dimensions:
            dim_section = self._create_dimensions_section(dimensions)
            content_layout.addWidget(dim_section)
        
        # Data types table
        data_types = data.get('data_types', {})
        if data_types:
            types_section = self._create_data_types_section(data_types)
            content_layout.addWidget(types_section)
        
        # Missing values table
        missing_values = data.get('missing_values', {})
        if missing_values:
            missing_section = self._create_missing_values_section(missing_values)
            content_layout.addWidget(missing_section)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    def _create_dimensions_section(self, dimensions: Dict[str, int]) -> QWidget:
        """Create the dimensions display section."""
        section_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        section_widget.setLayout(layout)
        
        # Section title
        title = QLabel("Dimensions")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title)
        
        # Dimensions info
        dim_text = QLabel(
            f"Rows: {dimensions.get('rows', 0):,}\n"
            f"Columns: {dimensions.get('columns', 0):,}"
        )
        dim_text.setStyleSheet("color: #BDBDBD; font-size: 13px; padding: 10px; background-color: #303030; border-radius: 5px;")
        layout.addWidget(dim_text)
        
        return section_widget
    
    def _create_data_types_section(self, data_types: Dict[str, str]) -> QWidget:
        """Create the data types table section (transposed - columns as headers)."""
        section_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        section_widget.setLayout(layout)
        
        # Section title
        title = QLabel("Data Types")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title)
        
        # Create table (transposed: 1 row, columns as headers)
        table = QTableWidget()
        table.setRowCount(1)
        table.setColumnCount(len(data_types))
        table.setHorizontalHeaderLabels(list(data_types.keys()))
        table.setVerticalHeaderLabels(["Data Type"])
        
        # Populate table
        for col_idx, (col_name, dtype) in enumerate(data_types.items()):
            dtype_item = QTableWidgetItem(str(dtype))
            dtype_item.setFlags(dtype_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            dtype_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(0, col_idx, dtype_item)
        
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
        
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
        layout.addWidget(table)
        return section_widget
    
    def _create_missing_values_section(self, missing_values: Dict[str, Dict[str, Any]]) -> QWidget:
        """Create the missing values table section (transposed - columns as headers)."""
        section_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        section_widget.setLayout(layout)
        
        # Section title
        title = QLabel("Missing Values")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title)
        
        # Create table (transposed: 2 rows, columns as headers)
        table = QTableWidget()
        table.setRowCount(2)
        table.setColumnCount(len(missing_values))
        table.setHorizontalHeaderLabels(list(missing_values.keys()))
        table.setVerticalHeaderLabels(["Missing Count", "Missing %"])
        
        # Populate table
        for col_idx, (col_name, mv_data) in enumerate(missing_values.items()):
            # Missing count (row 0)
            count_item = QTableWidgetItem(str(mv_data.get('count', 0)))
            count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(0, col_idx, count_item)
            
            # Missing percentage (row 1)
            percent = mv_data.get('percent', 0.0)
            percent_item = QTableWidgetItem(f"{percent:.2f}%")
            percent_item.setFlags(percent_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            percent_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            
            # Color code based on percentage
            if percent > 50:
                percent_item.setForeground(Qt.GlobalColor.red)
            elif percent > 25:
                percent_item.setForeground(Qt.GlobalColor.yellow)
            elif percent > 0:
                percent_item.setForeground(Qt.GlobalColor.cyan)
            
            table.setItem(1, col_idx, percent_item)
        
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
        
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
        layout.addWidget(table)
        return section_widget

