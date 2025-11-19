"""
Full Data Dialog Module
Non-modal dialog window displaying the complete dataset with sortable columns.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    # QHeaderView,  # COMMENTED OUT: Not used as a class (only referenced in stylesheet)
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pandas as pd


class NumericTableWidgetItem(QTableWidgetItem):
    """Custom QTableWidgetItem that sorts numeric values correctly."""
    
    def __init__(self, value):
        """Initialize with a numeric value."""
        super().__init__(str(value))
        self.numeric_value = float(value) if pd.notna(value) else None
    
    def __lt__(self, other):
        """Override comparison to sort numerically."""
        if isinstance(other, NumericTableWidgetItem):
            # Both are numeric items
            if self.numeric_value is None:
                return False  # None values go to the end
            if other.numeric_value is None:
                return True
            return self.numeric_value < other.numeric_value
        else:
            # Compare with non-numeric item - try to convert other to number
            try:
                other_val = float(other.text()) if other.text() else None
                if self.numeric_value is None:
                    return False
                if other_val is None:
                    return True
                return self.numeric_value < other_val
            except (ValueError, AttributeError):
                # Can't convert, treat as string comparison
                return str(self.text()) < str(other.text())


class FullDataDialog(QDialog):
    """Non-modal dialog window displaying the complete dataset in a sortable table."""
    
    def __init__(self, data: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.data = data
        
        # Set window flags to enable minimize and maximize buttons
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Make dialog non-modal so main window remains accessible
        self.setModal(False)
        
        self.setWindowTitle("Full Dataset View")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #212121;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        
        self._init_ui()
    
    def _init_ui(self):
        """Build and display the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Title and info
        title_label = QLabel("Full Dataset")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; padding-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Dataset info
        info_text = QLabel(
            f"Total: {len(self.data)} rows, {len(self.data.columns)} columns. "
            "Click column headers to sort."
        )
        info_text.setStyleSheet("color: #BDBDBD; font-size: 12px; padding-bottom: 10px;")
        layout.addWidget(info_text)
        
        # Create and populate table
        table_widget = self._create_table_widget()
        layout.addWidget(table_widget)
    
    def _create_table_widget(self) -> QTableWidget:
        """Create and populate the full data table widget."""
        # Create table
        table = QTableWidget()
        
        # Set dimensions
        table.setColumnCount(len(self.data.columns))
        table.setRowCount(len(self.data))
        
        # Set headers
        table.setHorizontalHeaderLabels([str(col) for col in self.data.columns])
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        # Style the header
        header = table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #424242;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        header.setDefaultSectionSize(120)
        header.setMinimumSectionSize(80)
        header.setStretchLastSection(True)
        
        # Calculate column widths (reuse logic from DataTableComponent)
        column_widths = self._calculate_column_widths()
        for i, width in enumerate(column_widths):
            if i < len(column_widths):
                table.setColumnWidth(i, width)
        
        # Populate all data rows
        for row_idx, (idx, row) in enumerate(self.data.iterrows()):
            for col_idx, val in enumerate(row):
                col_name = self.data.columns[col_idx]
                is_numeric = pd.api.types.is_numeric_dtype(self.data[col_name])
                
                if pd.isna(val):
                    item = QTableWidgetItem("")
                elif is_numeric:
                    # For numeric columns: use custom item class for proper numeric sorting
                    item = NumericTableWidgetItem(val)
                    # Align numeric values to the right
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    # For non-numeric columns: use standard string representation
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)
        
        # Style the table
        table.setStyleSheet("""
            QTableWidget {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
                gridline-color: #424242;
                selection-background-color: #424242;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:hover {
                background-color: #383838;
            }
        """)
        
        # Set row height
        table.verticalHeader().setVisible(False)
        for i in range(len(self.data)):
            table.setRowHeight(i, 40)
        
        # Disable editing
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Set selection behavior
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Enable scrollbars (default behavior, but ensure they're visible)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        return table
    
    def _calculate_column_widths(self) -> list:
        """Calculate optimal column widths based on content."""
        widths = []
        for col in self.data.columns:
            # Start with header width
            header_width = len(str(col)) * 8  # Approximate: 8 pixels per character
            
            # Check data widths in this column (sample first 100 rows for performance)
            if len(self.data) > 0:
                sample_size = min(100, len(self.data))
                max_data_width = max(
                    len(str(val)) if pd.notna(val) else 0 
                    for val in self.data[col].head(sample_size)
                )
                data_width = max_data_width * 7  # Approximate: 7 pixels per character
            else:
                data_width = 0
            
            # Use the maximum of header and data width, with minimum and maximum bounds
            width = max(header_width, data_width, 80)  # Minimum 80px
            width = min(width, 300)  # Maximum 300px to prevent too wide columns
            widths.append(int(width))
        
        return widths

