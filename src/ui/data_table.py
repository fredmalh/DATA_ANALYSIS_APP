"""
Data Table Component
Displays data in a tabular form.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    # QHBoxLayout,  # COMMENTED OUT: Not currently used, may be needed for future layouts
    QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, 
    # QHeaderView,  # COMMENTED OUT: Not used as a class (only referenced in stylesheet)
    # QScrollArea,  # COMMENTED OUT: Removed - QTableWidget handles its own scrolling now 
    # QSpacerItem,  # COMMENTED OUT: Not currently used, may be needed for future layouts
    QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
# from PyQt6.QtCore import QSize  # COMMENTED OUT: Not currently used, may be needed for future size calculations
import pandas as pd
from src.ui.full_data_dialog import FullDataDialog


class DataTableComponent:
    """Component for displaying data in a table."""
    
    def __init__(self, data: pd.DataFrame, parent=None):
        self.data = data
        self.parent = parent
        self.column_widths = self._calculate_column_widths()
        self.full_data_dialog = None  # Keep reference to prevent garbage collection
        
    def build(self) -> tuple[QWidget, QWidget]:
        """Build the data table UI with fixed headers showing first 10 rows.
        
        Returns:
            tuple: (table_container, button_container)
        """
        # Calculate number of rows to display (max 10)
        rows_to_show = min(10, len(self.data))
        total_rows = len(self.data)
        
        # Main container widget for table
        table_container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        table_container.setLayout(layout)
        
        # Info text
        if total_rows > 10:
            info_text = QLabel(
                f"Showing first {rows_to_show} of {total_rows} rows, {len(self.data.columns)} columns"
            )
        else:
            info_text = QLabel(
                f"Showing {rows_to_show} rows, {len(self.data.columns)} columns"
            )
        info_text.setStyleSheet("color: #BDBDBD; font-size: 12px;")
        layout.addWidget(info_text)
        
        # Create table widget
        table_widget = self._create_table_widget(rows_to_show)
        
        # Add table directly to container - let QTableWidget handle its own scrolling
        layout.addWidget(table_widget)
        
        # Create separate container for the button
        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(10, 0, 10, 10)
        button_layout.setSpacing(0)
        button_container.setLayout(button_layout)
        
        # "See All Data" button in its own container
        see_all_button = QPushButton("See All Data")
        see_all_button.setStyleSheet("""
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
        see_all_button.clicked.connect(self._open_full_data_dialog)
        button_layout.addWidget(see_all_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return table_container, button_container
    
    def _create_table_widget(self, rows_to_show: int) -> QTableWidget:
        """Create and populate the table widget."""
        # Create table
        table = QTableWidget()
        
        # Set column count
        table.setColumnCount(len(self.data.columns))
        table.setRowCount(rows_to_show)
        
        # Set headers
        table.setHorizontalHeaderLabels([str(col) for col in self.data.columns])
        
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
        header.setDefaultSectionSize(100)
        header.setMinimumSectionSize(80)
        
        # Set column widths
        for i, width in enumerate(self.column_widths):
            if i < len(self.column_widths):
                table.setColumnWidth(i, width)
        
        # Populate data (first rows_to_show rows)
        for row_idx, (idx, row) in enumerate(self.data.head(rows_to_show).iterrows()):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val) if pd.notna(val) else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
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
        for i in range(rows_to_show):
            table.setRowHeight(i, 50)
        
        # Disable editing
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Set selection behavior
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Enable table's own scrollbars - let QTableWidget handle scrolling natively
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Only horizontal scrolling needed
        
        # Configure horizontal scroll bar for better mouse wheel scrolling
        # Single step: distance scrolled per wheel click (default is too small)
        # Page step: distance scrolled when clicking scroll bar track
        horizontal_scrollbar = table.horizontalScrollBar()
        horizontal_scrollbar.setSingleStep(50)  # Scroll 50px per wheel notch (was ~1-2px)
        horizontal_scrollbar.setPageStep(200)   # Scroll 200px when clicking track
        
        # Calculate minimum width based on column widths
        total_width = sum(self.column_widths) if self.column_widths else 800
        table.setMinimumWidth(total_width)
        
        # Set explicit size constraints to ensure proper height calculation
        # Header height + (rows * row height)
        header_height = 40
        table_height = header_height + (rows_to_show * 50)
        table.setMinimumHeight(table_height)
        table.setMaximumHeight(table_height)
        
        # Set size policy: allow horizontal expansion but keep height fixed
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        size_policy.setHorizontalStretch(1)  # Allow horizontal stretching
        size_policy.setVerticalStretch(0)
        table.setSizePolicy(size_policy)
        
        return table
    
    def _open_full_data_dialog(self):
        """Open a dialog window displaying the complete dataset."""
        if self.data is None or self.data.empty:
            return
        
        # Check if dialog is already open
        if self.full_data_dialog is not None and self.full_data_dialog.isVisible():
            # Show warning message
            msg_box = QMessageBox(self.parent)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Dialog Already Open")
            msg_box.setText("The Full Dataset View dialog is already open.")
            msg_box.setInformativeText("Please use the existing window or close it before opening a new one.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            return
        
        # Create and show dialog (non-modal, so main window remains accessible)
        self.full_data_dialog = FullDataDialog(self.data, self.parent)
        self.full_data_dialog.show()
    
    def _calculate_column_widths(self) -> list:
        """Calculate optimal column widths based on content."""
        widths = []
        for col in self.data.columns:
            # Start with header width
            header_width = len(str(col)) * 8  # Approximate: 8 pixels per character
            
            # Check data widths in this column
            if len(self.data) > 0:
                max_data_width = max(
                    len(str(val)) if pd.notna(val) else 0 
                    for val in self.data[col].head(100)  # Check first 100 rows
                )
                data_width = max_data_width * 7  # Approximate: 7 pixels per character
            else:
                data_width = 0
            
            # Use the maximum of header and data width, with minimum and maximum bounds
            width = max(header_width, data_width, 80)  # Minimum 80px
            width = min(width, 300)  # Maximum 300px to prevent too wide columns
            widths.append(int(width))
        
        return widths
