"""
Main Window Module
Main application window with file upload and data display.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMessageBox, QFrame, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
from typing import Optional
import pandas as pd
from src.file_handler import FileHandler
from src.ui.data_table import DataTableComponent
from src.ui.column_selection_dialog import ColumnSelectionDialog
from src.analysis.registry import registry
from src.analysis.dataset_overview import DatasetOverviewAnalyzer
from src.analysis.basic_statistics import BasicStatisticsAnalyzer
from src.analysis.correlation import CorrelationAnalyzer
from src.analysis.optimization import OptimizationAnalyzer
from src.ui.analysis_factory import AnalysisDialogFactory
from src.ui.optimization_dialog import OptimizationDialog


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
        
        # Register analyzers
        self._register_analyzers()
        
        self._init_ui()
    
    def _register_analyzers(self):
        """Register all available analyzers."""
        registry.register('dataset_overview', DatasetOverviewAnalyzer)
        registry.register('basic_statistics', BasicStatisticsAnalyzer)
        registry.register('correlation', CorrelationAnalyzer)
        registry.register('optimization', OptimizationAnalyzer)
    
    def _init_ui(self):
        """Build and display the main window UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)  # Reduced spacing for more compact layout, especially around section titles
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
        preview_font.setPointSize(14)
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        preview_label.setStyleSheet("color: white; padding-top: 5px; padding-bottom: 3px;")
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
        tools_font.setPointSize(14)
        tools_font.setBold(True)
        tools_label.setFont(tools_font)
        tools_label.setStyleSheet("color: white; padding-top: 5px; padding-bottom: 3px;")
        main_layout.addWidget(tools_label)
        
        # Analysis buttons
        analysis_buttons = self._create_analysis_buttons()
        main_layout.addWidget(analysis_buttons)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
    
    def _create_section_container(self, min_height: int = 150, max_height: int = 200, 
                                   min_width: Optional[int] = None, max_width: Optional[int] = None,
                                   object_name: Optional[str] = None, stylesheet: Optional[str] = None) -> QWidget:
        """Create a standardized section container widget.
        
        Args:
            min_height: Minimum height of the container (default: 150)
            max_height: Maximum height of the container (default: 200)
            min_width: Optional minimum width constraint
            max_width: Optional maximum width constraint
            object_name: Optional object name for CSS styling
            stylesheet: Optional stylesheet string to apply
        
        Returns:
            QWidget: Configured container widget
        """
        container = QWidget()
        container.setMinimumHeight(min_height)
        container.setMaximumHeight(max_height)
        
        if min_width is not None:
            container.setMinimumWidth(min_width)
        if max_width is not None:
            container.setMaximumWidth(max_width)
        if object_name:
            container.setObjectName(object_name)
        if stylesheet:
            container.setStyleSheet(stylesheet)
        
        return container
    
    def _create_centered_label(self, text: str, font_size: int, color: str = "white",
                               font_weight: Optional[QFont.Weight] = None,
                               additional_styles: str = "") -> QLabel:
        """Create a centered label with standardized styling.
        
        Args:
            text: Label text content
            font_size: Font point size
            color: Text color (default: "white")
            font_weight: Optional font weight (e.g., QFont.Weight.Medium)
            additional_styles: Additional CSS styles to append
        
        Returns:
            QLabel: Configured and styled label widget
        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont()
        font.setPointSize(font_size)
        if font_weight:
            font.setWeight(font_weight)
        label.setFont(font)
        
        style = f"color: {color}; background-color: transparent; {additional_styles}"
        label.setStyleSheet(style)
        
        return label
    
    def _create_drop_zone(self) -> QWidget:
        """Create the file upload/drop zone with side-by-side layout.
        
        Layout structure:
        - Main container: Horizontal layout with 15px spacing
        - Left section (2/3 width): Drop zone with grey background
        - Middle section (minimal width): "or" separator text
        - Right section (1/3 width): Upload button
        
        Spacing rationale:
        - Container spacing (15px): Provides visual separation between sections
        - Content margins (20px): Standard padding for interactive elements (drop zone, button)
        - Separator margins (10px horizontal): Minimal padding for text-only separator
        - Content spacing (15px): Vertical spacing between icon and text in drop zone
        - Container layout spacing (0px): No spacing needed within containers (content handles spacing)
        """
        # Constants for consistent sizing
        SECTION_MIN_HEIGHT = 150
        SECTION_MAX_HEIGHT = 200
        CONTAINER_SPACING = 15  # Horizontal spacing between main sections
        CONTENT_MARGINS = 20  # Standard padding for interactive content areas
        CONTENT_SPACING = 15  # Vertical spacing between elements in drop zone
        SEPARATOR_H_MARGINS = 10  # Horizontal margins for "or" separator
        SEPARATOR_MIN_WIDTH = 40
        SEPARATOR_MAX_WIDTH = 60
        ICON_FONT_SIZE = 32
        TEXT_FONT_SIZE = 16
        SEPARATOR_FONT_SIZE = 14
        
        # Create main container with horizontal layout
        container = QWidget()
        container_layout = QHBoxLayout()
        container_layout.setSpacing(CONTAINER_SPACING)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        
        # Left section: Drag and drop zone (2/3 width)
        drop_container = self._create_section_container(
            min_height=SECTION_MIN_HEIGHT,
            max_height=SECTION_MAX_HEIGHT,
            object_name="dropContainer",
            stylesheet="""
                QWidget#dropContainer {
                    border: 2px solid #424242;
                    border-radius: 15px;
                    background-color: #303030;
                }
            """
        )
        
        # Container layout: no spacing/margins (content widget handles its own spacing)
        drop_container_layout = QVBoxLayout()
        drop_container_layout.setSpacing(0)
        drop_container_layout.setContentsMargins(0, 0, 0, 0)
        drop_container.setLayout(drop_container_layout)
        
        # Create DropZoneWidget inside container (for drag/drop functionality)
        drop_zone = DropZoneWidget(drop_container, on_file_dropped=self.load_file)
        drop_zone.setStyleSheet("background-color: transparent;")
        
        # Content layout: spacing and margins for visual hierarchy
        drop_layout = QVBoxLayout()
        drop_layout.setSpacing(CONTENT_SPACING)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.setContentsMargins(CONTENT_MARGINS, CONTENT_MARGINS, CONTENT_MARGINS, CONTENT_MARGINS)
        drop_zone.setLayout(drop_layout)
        
        # Text label (on top)
        drag_text = self._create_centered_label(
            text="Drag and drop files here",
            font_size=TEXT_FONT_SIZE,
            color="white",
            font_weight=QFont.Weight.Medium
        )
        drop_layout.addWidget(drag_text)
        
        # Upload icon (using text as icon placeholder, below text)
        icon_label = self._create_centered_label(
            text="📤",
            font_size=ICON_FONT_SIZE,
            color="#64B5F6"
        )
        drop_layout.addWidget(icon_label)
        
        # Add drop zone to container layout
        drop_container_layout.addWidget(drop_zone)
        
        # Add drop container to main container with stretch factor 3 (3/4 width)
        container_layout.addWidget(drop_container, stretch=3)
        
        # Middle section: "or" separator
        or_container = self._create_section_container(
            min_height=SECTION_MIN_HEIGHT,
            max_height=SECTION_MAX_HEIGHT,
            min_width=SEPARATOR_MIN_WIDTH,
            max_width=SEPARATOR_MAX_WIDTH
        )
        
        # Separator layout: minimal margins, centered alignment
        or_layout = QVBoxLayout()
        or_layout.setSpacing(0)
        or_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_layout.setContentsMargins(SEPARATOR_H_MARGINS, 0, SEPARATOR_H_MARGINS, 0)
        or_container.setLayout(or_layout)
        
        or_text = self._create_centered_label(
            text="or",
            font_size=SEPARATOR_FONT_SIZE,
            color="#BDBDBD"
        )
        or_layout.addWidget(or_text)
        
        # Add "or" container with minimal stretch (just enough for the text)
        container_layout.addWidget(or_container, stretch=0)
        
        # Right section: Upload button (1/3 width)
        upload_container = self._create_section_container(
            min_height=SECTION_MIN_HEIGHT,
            max_height=SECTION_MAX_HEIGHT
        )
        
        # Upload layout: standard content margins, centered alignment
        upload_layout = QVBoxLayout()
        upload_layout.setSpacing(0)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.setContentsMargins(CONTENT_MARGINS, CONTENT_MARGINS, CONTENT_MARGINS, CONTENT_MARGINS)
        upload_container.setLayout(upload_layout)
        
        # Upload button
        upload_button = QPushButton("Upload File")
        # upload_button.setIcon(QIcon.fromTheme("document-open"))  # COMMENTED OUT: QIcon.fromTheme() doesn't work on Windows (Linux/Unix only). May be useful for cross-platform icon support in the future.
        upload_button.clicked.connect(self._on_upload_clicked)
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                min-height: 48px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
        """)
        upload_layout.addWidget(upload_button)
        
        # Add upload container to main container with stretch factor 1 (1/4 width)
        container_layout.addWidget(upload_container, stretch=1)
        
        return container
    
    def _create_analysis_buttons(self) -> QWidget:
        """Create analysis buttons section."""
        buttons_widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)
        buttons_widget.setLayout(layout)
        
        # Drop Columns button
        drop_columns_button = QPushButton("Drop Columns")
        drop_columns_button.setEnabled(True)
        drop_columns_button.clicked.connect(self._on_drop_columns_clicked)
        layout.addWidget(drop_columns_button)
        
        # Dataset Overview button
        overview_button = QPushButton("Dataset Overview")
        overview_button.setEnabled(True)
        overview_button.clicked.connect(self._on_dataset_overview_clicked)
        layout.addWidget(overview_button)
        
        # Basic Statistics button
        basic_stats_button = QPushButton("Basic Statistics")
        basic_stats_button.setEnabled(True)
        basic_stats_button.clicked.connect(self._on_basic_statistics_clicked)
        layout.addWidget(basic_stats_button)
        
        # Correlation button
        correlation_button = QPushButton("Correlation")
        correlation_button.setEnabled(True)
        correlation_button.clicked.connect(self._on_correlation_clicked)
        layout.addWidget(correlation_button)
        
        # 2D Plot button
        plot_2d_button = QPushButton("2D Plot")
        plot_2d_button.setEnabled(True)
        plot_2d_button.clicked.connect(self._on_plot_2d_clicked)
        layout.addWidget(plot_2d_button)
        
        # Optimization button
        optimization_button = QPushButton("Optimization")
        optimization_button.setEnabled(True)
        optimization_button.clicked.connect(self._on_optimization_clicked)
        layout.addWidget(optimization_button)
        
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
    
    def _on_drop_columns_clicked(self):
        """Handle drop columns button click."""
        if self.data is None or self.data.empty:
            self._show_error("No data loaded. Please upload a file first.")
            return
        
        # Open column selection dialog
        dialog = ColumnSelectionDialog(list(self.data.columns), self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            columns_to_drop = dialog.get_selected_columns()
            
            if columns_to_drop:
                # Drop the selected columns
                try:
                    self.data = self.data.drop(columns=columns_to_drop)
                    
                    # Refresh the data display
                    self._refresh_data_display()
                    
                    # Show success message
                    self.statusBar().showMessage(
                        f"Successfully dropped {len(columns_to_drop)} column(s). "
                        f"Remaining: {len(self.data.columns)} columns, {len(self.data)} rows",
                        3000
                    )
                except Exception as e:
                    self._show_error(f"Error dropping columns: {str(e)}")
    
    def _refresh_data_display(self):
        """Refresh the data table display after data modification."""
        if self.data is None or self.data.empty:
            self._reset_table_container()
            return
        
        # Clear current table
        self._clear_table_container()
        
        # Recreate data table with updated data
        try:
            self.data_table_widget = DataTableComponent(self.data, self)
            table_container, button_container = self.data_table_widget.build()
            self.table_layout.addWidget(table_container)
            self.table_layout.addWidget(button_container)
        except Exception as e:
            self._show_error(f"Error displaying updated data: {str(e)}")
    
    def _on_dataset_overview_clicked(self):
        """Handle dataset overview button click."""
        if self.data is None or self.data.empty:
            self._show_error("No data loaded. Please upload a file first.")
            return
        
        # Get analyzer instance
        analyzer = registry.create_analyzer_instance('dataset_overview')
        if analyzer is None:
            self._show_error("Dataset overview analyzer not available.")
            return
        
        # Perform analysis
        result = analyzer.analyze(self.data)
        
        # Create and show dialog
        dialog = AnalysisDialogFactory.create_dialog(
            "Dataset Overview",
            result,
            result_type=analyzer.get_result_type(),
            parent=self
        )
        dialog.show()
    
    def _on_basic_statistics_clicked(self):
        """Handle basic statistics button click."""
        if self.data is None or self.data.empty:
            self._show_error("No data loaded. Please upload a file first.")
            return
        
        # Get analyzer instance
        analyzer = registry.create_analyzer_instance('basic_statistics')
        if analyzer is None:
            self._show_error("Basic statistics analyzer not available.")
            return
        
        # Perform analysis
        result = analyzer.analyze(self.data)
        
        # Create and show dialog
        dialog = AnalysisDialogFactory.create_dialog(
            "Basic Statistics",
            result,
            result_type=analyzer.get_result_type(),
            parent=self
        )
        dialog.show()
    
    def _on_correlation_clicked(self):
        """Handle correlation button click."""
        if self.data is None or self.data.empty:
            self._show_error("No data loaded. Please upload a file first.")
            return
        
        # Get analyzer instance
        analyzer = registry.create_analyzer_instance('correlation')
        if analyzer is None:
            self._show_error("Correlation analyzer not available.")
            return
        
        # Perform analysis
        result = analyzer.analyze(self.data)
        
        # Check if analysis was successful
        if not result.get('success', False):
            self._show_error(result.get('error', 'Unknown error computing correlations.'))
            return
        
        # Create and show dialog
        dialog = AnalysisDialogFactory.create_dialog(
            "Correlation Analysis",
            result,
            result_type=analyzer.get_result_type(),
            parent=self
        )
        dialog.show()
    
    def _on_plot_2d_clicked(self):
        """Handle 2D plot button click."""
        if self.data is None or self.data.empty:
            self._show_error("No data loaded. Please upload a file first.")
            return
        
        # Get numeric columns
        import numpy as np
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            self._show_error("Need at least 2 numeric columns to create a 2D plot.")
            return
        
        # Prepare result data for dialog
        result_data = {
            'success': True,
            'data': self.data,
            'numeric_columns': numeric_cols,
            'summary': f"Select X and Y variables to plot. {len(numeric_cols)} numeric columns available."
        }
        
        # Create and show dialog
        from src.ui.plot_2d_dialog import Plot2DDialog
        dialog = Plot2DDialog("2D Plot", result_data, self)
        dialog.show()
    
    def _on_optimization_clicked(self):
        """Handle optimization button click."""
        if self.data is None or self.data.empty:
            self._show_error("No data loaded. Please upload a file first.")
            return
        
        # Check for numeric columns
        numeric_cols = [col for col in self.data.columns 
                       if pd.api.types.is_numeric_dtype(self.data[col])]
        
        if len(numeric_cols) < 2:  # Need at least 1 target + 1 input
            self._show_error(
                "Not enough numeric columns for optimization. "
                "Need at least 2 numeric columns (1 target + 1 input)."
            )
            return
        
        # Open optimization configuration dialog
        dialog = OptimizationDialog(self.data, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get configuration
            config = dialog.get_configuration()
            
            try:
                # Create analyzer instance
                analyzer = OptimizationAnalyzer()
                
                # Run optimization
                result_data = analyzer.analyze(
                    data=self.data,
                    target_variables=config['target_variables'],
                    optimization_directions=config['optimization_directions'],
                    constraints=config['constraints'],
                    weights=config['weights'],
                    input_variables=config['input_variables'],
                    top_n=10
                )
                
                # Add config to result_data for back button functionality
                result_data['config'] = config
                
                # Display results using factory
                result_dialog = AnalysisDialogFactory.create_dialog(
                    title="Optimization Results",
                    result_data=result_data,
                    result_type='optimization',
                    parent=self
                )
                result_dialog.show()
                
            except Exception as e:
                self._show_error(f"Error during optimization: {str(e)}")
    
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
