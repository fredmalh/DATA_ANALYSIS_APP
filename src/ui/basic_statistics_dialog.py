"""
Basic Statistics Dialog Module
Dialog for displaying basic statistics results.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any
from src.ui.analysis_dialogs import BaseAnalysisDialog


class BasicStatisticsDialog(BaseAnalysisDialog):
    """Dialog for displaying basic statistics results."""
    
    def _build_content(self) -> QWidget:
        """Build content for basic statistics results."""
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
        constant_vars = self.result_data.get('constant_vars', [])
        near_constant_vars = self.result_data.get('near_constant_vars', [])
        
        # Warning section for constant/near-constant variables
        if constant_vars or near_constant_vars:
            warning_section = self._create_warning_section(constant_vars, near_constant_vars)
            content_layout.addWidget(warning_section)
        
        # Statistics table
        if data:
            stats_section = self._create_statistics_table(data)
            content_layout.addWidget(stats_section)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    def _create_warning_section(self, constant_vars: list, near_constant_vars: list) -> QWidget:
        """Create warning section for constant/near-constant variables."""
        section_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        section_widget.setLayout(layout)
        
        # Section title
        title = QLabel("⚠️ Constant / Near-Constant Variables")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ff9800; padding-bottom: 5px;")
        layout.addWidget(title)
        
        warning_text = ""
        if constant_vars:
            warning_text += f"Constant variables (single unique value): {', '.join(constant_vars)}\n"
        if near_constant_vars:
            warning_text += f"Near-constant variables (<1% unique values): {', '.join(near_constant_vars)}"
        
        warning_label = QLabel(warning_text)
        warning_label.setStyleSheet("color: #ff9800; font-size: 12px; padding: 10px; background-color: #3e2723; border-radius: 5px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        return section_widget
    
    def _create_statistics_table(self, statistics: Dict[str, Dict[str, Any]]) -> QWidget:
        """Create the statistics table (transposed - columns as headers)."""
        section_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        section_widget.setLayout(layout)
        
        # Section title
        title = QLabel("Basic Statistics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title)
        
        # Define row labels (statistics)
        row_labels = [
            "Mean", "Min", "Q1 (25%)", "Median (50%)", "Q3 (75%)", 
            "Max", "Skewness", "Kurtosis", "Cardinality"
        ]
        
        # Create table (transposed: statistics as rows, columns as headers)
        table = QTableWidget()
        table.setRowCount(len(row_labels))
        table.setColumnCount(len(statistics))
        table.setHorizontalHeaderLabels(list(statistics.keys()))
        table.setVerticalHeaderLabels(row_labels)
        
        # Populate table
        for col_idx, (col_name, col_stats) in enumerate(statistics.items()):
            # Mean (row 0)
            mean_val = col_stats.get('mean')
            mean_item = self._create_table_item(mean_val, 4)
            table.setItem(0, col_idx, mean_item)
            
            # Min (row 1)
            min_val = col_stats.get('min')
            min_item = self._create_table_item(min_val, 4)
            table.setItem(1, col_idx, min_item)
            
            # Q1 (row 2)
            q1_val = col_stats.get('q1')
            q1_item = self._create_table_item(q1_val, 4)
            table.setItem(2, col_idx, q1_item)
            
            # Median (row 3)
            median_val = col_stats.get('median')
            median_item = self._create_table_item(median_val, 4)
            table.setItem(3, col_idx, median_item)
            
            # Q3 (row 4)
            q3_val = col_stats.get('q3')
            q3_item = self._create_table_item(q3_val, 4)
            table.setItem(4, col_idx, q3_item)
            
            # Max (row 5)
            max_val = col_stats.get('max')
            max_item = self._create_table_item(max_val, 4)
            table.setItem(5, col_idx, max_item)
            
            # Skewness (row 6)
            skew_val = col_stats.get('skewness')
            skew_item = self._create_table_item(skew_val, 4)
            table.setItem(6, col_idx, skew_item)
            
            # Kurtosis (row 7)
            kurt_val = col_stats.get('kurtosis')
            kurt_item = self._create_table_item(kurt_val, 4)
            table.setItem(7, col_idx, kurt_item)
            
            # Cardinality (row 8)
            card_val = col_stats.get('cardinality')
            card_item = self._create_table_item(card_val, 0)
            table.setItem(8, col_idx, card_item)
        
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
    
    def _create_table_item(self, value: Any, decimals: int = 4) -> QTableWidgetItem:
        """
        Create a table item with proper formatting.
        
        Args:
            value: Value to display
            decimals: Number of decimal places (0 for integers)
            
        Returns:
            QTableWidgetItem
        """
        if value is None:
            item = QTableWidgetItem("N/A")
        elif isinstance(value, (int, float)):
            if decimals == 0:
                item = QTableWidgetItem(str(int(value)))
            else:
                item = QTableWidgetItem(f"{value:.{decimals}f}")
        else:
            item = QTableWidgetItem(str(value))
        
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        return item

