"""
Main Window Module
Main application window with file upload and data display.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent
from typing import Optional
import pandas as pd
from src.file_handler import FileHandler
from src.ui.data_table import DataTableComponent


class FileLoaderThread(QThread):
    """Thread for loading files in the background."""
    finished = pyqtSignal(object, object)  # DataFrame, error_message (str or None)
    
    def __init__(self, file_handler, file_path):
        super().__init__()
        self.file_handler = file_handler
        self.file_path = file_path
    
    def run(self):
        df, error = self.file_handler.load_file(self.file_path)
        self.finished.emit(df, error)


class DropZoneWidget(QWidget):
    """Custom widget that handles drag and drop of files."""
    
    def __init__(self, parent=None, on_file_dropped=None):
        super().__init__(parent)
        self.on_file_dropped = on_file_dropped
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event - accept if files are being dragged."""
        if event.mimeData().hasUrls():
            # Check if at least one file has a supported extension
            urls = event.mimeData().urls()
            supported_extensions = {'.csv', '.xlsx', '.xls', '.xml'}
            for url in urls:
                file_path = url.toLocalFile()
                if file_path:
                    from pathlib import Path
                    extension = Path(file_path).suffix.lower()
                    if extension in supported_extensions:
                        event.acceptProposedAction()
                        return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event - extract file path and call callback."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()  # Take the first file
                if file_path and self.on_file_dropped:
                    self.on_file_dropped(file_path)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()


class MainWindow(QMainWindow):
    """Main application window component."""
    
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.data: Optional[pd.DataFrame] = None
        self.data_table_widget = None
        self.loader_thread = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Build and display the main window UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("Data Analysis Application")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; padding-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Divider
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        divider1.setStyleSheet("color: #757575; background-color: #757575; min-height: 1px; max-height: 1px;")
        main_layout.addWidget(divider1)
        
        # Drop zone / Upload area
        drop_zone = self._create_drop_zone()
        main_layout.addWidget(drop_zone)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        divider2.setStyleSheet("color: #757575; background-color: #757575; min-height: 1px; max-height: 1px;")
        main_layout.addWidget(divider2)
        
        # Data Preview section
        preview_label = QLabel("Data Preview")
        preview_font = QFont()
        preview_font.setPointSize(18)
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        preview_label.setStyleSheet("color: white; padding-top: 10px; padding-bottom: 5px;")
        main_layout.addWidget(preview_label)
        
        # Table container (placeholder)
        self.table_container = QWidget()
        self.table_container.setMinimumHeight(100)
        self.table_layout = QVBoxLayout()
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_container.setLayout(self.table_layout)
        
        # Initial placeholder text
        placeholder_label = QLabel("No data loaded. Please upload a file.")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: #BDBDBD; font-size: 16px; padding: 20px;")
        self.table_layout.addWidget(placeholder_label)
        
        main_layout.addWidget(self.table_container)
        
        # Divider
        divider3 = QFrame()
        divider3.setFrameShape(QFrame.Shape.HLine)
        divider3.setFrameShadow(QFrame.Shadow.Sunken)
        divider3.setStyleSheet("color: #757575; background-color: #757575; min-height: 1px; max-height: 1px;")
        main_layout.addWidget(divider3)
        
        # Analysis Tools section
        tools_label = QLabel("Analysis Tools")
        tools_font = QFont()
        tools_font.setPointSize(18)
        tools_font.setBold(True)
        tools_label.setFont(tools_font)
        tools_label.setStyleSheet("color: white; padding-top: 10px; padding-bottom: 5px;")
        main_layout.addWidget(tools_label)
        
        # Analysis buttons
        analysis_buttons = self._create_analysis_buttons()
        main_layout.addWidget(analysis_buttons)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
    
    def _create_drop_zone(self) -> QWidget:
        """Create the file upload/drop zone."""
        drop_zone = DropZoneWidget(self, on_file_dropped=self.load_file)
        drop_zone.setMaximumHeight(200)  # Set maximum height
        drop_zone.setObjectName("dropZone")  # Set object name for specific styling
        drop_zone.setStyleSheet("""
            QWidget#dropZone {
                border: 2px solid #64B5F6;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        drop_zone.setLayout(layout)
        
        # Upload icon (using text as icon placeholder)
        icon_label = QLabel("📤")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(32)  # Reduced from 48
        icon_label.setFont(icon_font)
        icon_label.setStyleSheet("color: #64B5F6;")
        layout.addWidget(icon_label)
        
        # Text labels
        drag_text = QLabel("Drag and drop files here")
        drag_font = QFont()
        drag_font.setPointSize(16)  # Reduced from 20
        drag_font.setWeight(QFont.Weight.Medium)
        drag_text.setFont(drag_font)
        drag_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_text.setStyleSheet("color: white;")
        layout.addWidget(drag_text)
        
        or_text = QLabel("or")
        or_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_text.setStyleSheet("color: #BDBDBD; font-size: 14px;")
        layout.addWidget(or_text)
        
        # Upload button
        upload_button = QPushButton("Upload File")
        upload_button.setIcon(QIcon.fromTheme("document-open"))
        upload_button.clicked.connect(self._on_upload_clicked)
        upload_button.setStyleSheet("""
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
        layout.addWidget(upload_button)
        
        return drop_zone
    
    def _create_analysis_buttons(self) -> QWidget:
        """Create analysis buttons section."""
        buttons_widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)
        buttons_widget.setLayout(layout)
        
        # Analysis buttons (enabled, functionality to be implemented)
        for i in range(1, 4):
            button = QPushButton(f"Analysis {i}")
            button.setEnabled(True)  # Enable buttons so they show blue
            # Functionality to be implemented later
            # Use a lambda with default argument to capture the correct value
            button.clicked.connect(lambda checked, num=i: self._on_analysis_clicked(num))
            layout.addWidget(button)
        
        layout.addStretch()
        return buttons_widget
    
    def _on_upload_clicked(self):
        """Handle upload button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "Data Files (*.csv *.xlsx *.xls *.xml);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """Load a file and display its data."""
        # Clear previous table
        self._clear_table_container()
        
        # Show loading indicator
        loading_widget = QWidget()
        loading_layout = QVBoxLayout()
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.setSpacing(10)
        loading_widget.setLayout(loading_layout)
        
        loading_label = QLabel("Loading file...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: #BDBDBD; font-size: 16px;")
        loading_layout.addWidget(loading_label)
        
        self.table_layout.addWidget(loading_widget)
        
        # Load file in a thread to avoid blocking UI
        self.loader_thread = FileLoaderThread(self.file_handler, file_path)
        self.loader_thread.finished.connect(self._on_file_loaded)
        self.loader_thread.start()
    
    def _on_file_loaded(self, df: Optional[pd.DataFrame], error: Optional[str]):
        """Handle file loading completion."""
        self._clear_table_container()
        
        if error:
            self._show_error(error)
            self._reset_table_container()
            return
        
        if df is None:
            self._show_error("The file could not be parsed. Please check the file format.")
            self._reset_table_container()
            return
        
        if df.empty:
            self._show_error("The file appears to be empty or contains no data.")
            self._reset_table_container()
            return
        
        self.data = df
        
        # Create and display data table
        try:
            self.data_table_widget = DataTableComponent(self.data, self)
            table_container, button_container = self.data_table_widget.build()
            # Add table container first
            self.table_layout.addWidget(table_container)
            # Add button container immediately after
            self.table_layout.addWidget(button_container)
            
            # Show success message
            self.statusBar().showMessage(
                f"Successfully loaded {len(df)} rows and {len(df.columns)} columns",
                3000
            )
        except Exception as e:
            self._show_error(f"Error displaying data: {str(e)}")
    
    def _clear_table_container(self):
        """Clear all widgets from table container."""
        while self.table_layout.count():
            child = self.table_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _reset_table_container(self):
        """Reset the table container to empty state."""
        self._clear_table_container()
        placeholder_label = QLabel("No data loaded. Please upload a file.")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: #BDBDBD; font-size: 16px; padding: 20px;")
        self.table_layout.addWidget(placeholder_label)
    
    def _on_analysis_clicked(self, analysis_num: int):
        """Handle analysis button click (placeholder for future implementation)."""
        # Placeholder - functionality to be implemented
        self.statusBar().showMessage(f"Analysis {analysis_num} - Functionality to be implemented", 2000)
    
    def _show_error(self, message: str):
        """Show an error dialog."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
