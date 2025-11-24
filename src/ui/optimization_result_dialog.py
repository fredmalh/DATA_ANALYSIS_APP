"""
Optimization Result Dialog Module
Dialog for displaying optimization results.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QScrollArea, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any, Optional
import pandas as pd
from src.ui.analysis_dialogs import BaseAnalysisDialog
from src.ui.optimization_dialog import OptimizationDialog


class OptimizationResultDialog(BaseAnalysisDialog):
    """Dialog for displaying optimization results."""
    
    def __init__(self, title: str, result_data: Dict[str, Any], parent=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the optimization result dialog.
        
        Args:
            title: Dialog window title
            result_data: Dictionary containing analysis results
            parent: Parent window
            config: Configuration used for optimization (for back button)
        """
        self.optimization_config = config
        self.results_df = None  # Store the reordered DataFrame for export
        super().__init__(title, result_data, parent)
    
    def _init_ui(self):
        """Override to add back button."""
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
        
        # Content area
        self.content_widget = self._build_content()
        if self.content_widget:
            layout.addWidget(self.content_widget)
        
        # Buttons (Export, Back and Close)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Export to Excel button
        if self.results_df is not None and not self.results_df.empty:
            export_button = QPushButton("Export to Excel")
            export_button.setStyleSheet("""
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #388e3c;
                }
                QPushButton:pressed {
                    background-color: #1b5e20;
                }
            """)
            export_button.clicked.connect(self._on_export_clicked)
            button_layout.addWidget(export_button)
        
        # Back button (only show if config is available)
        if self.optimization_config:
            back_button = QPushButton("Back")
            back_button.setStyleSheet("""
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
                QPushButton:pressed {
                    background-color: #303030;
                }
            """)
            back_button.clicked.connect(self._on_back_clicked)
            button_layout.addWidget(back_button)
        
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
        """Build content for optimization results."""
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
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_widget.setLayout(content_layout)
        
        # Get results DataFrame
        results_df = self.result_data.get('data')
        if results_df is None or results_df.empty:
            error_label = QLabel("No results to display.")
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setWordWrap(True)
            content_layout.addWidget(error_label)
            content_widget.setLayout(content_layout)
            scroll_area.setWidget(content_widget)
            return scroll_area
        
        # Reorder columns to match original data order, with composite score at the end
        reordered_df = self._reorder_columns(results_df)
        self.results_df = reordered_df.copy()  # Store for export
        
        # Create results table
        results_table = self._create_results_table(reordered_df)
        content_layout.addWidget(results_table)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    def _reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorder DataFrame columns to match original data order, with composite score at the end.
        
        Args:
            df: Results DataFrame from optimization
            
        Returns:
            DataFrame with reordered columns
        """
        if df is None or df.empty:
            return df
        
        # Get original data column order from parent chain
        original_columns = []
        try:
            from src.ui.main_window import MainWindow
            from src.ui.optimization_dialog import OptimizationDialog
            
            parent = self.parent()
            
            # Walk up the parent chain to find MainWindow
            # Result dialog -> Optimization dialog -> MainWindow
            while parent:
                if isinstance(parent, MainWindow):
                    if parent.data is not None and not parent.data.empty:
                        original_columns = list(parent.data.columns)
                    break
                # If parent is OptimizationDialog, try to get its parent
                elif isinstance(parent, OptimizationDialog):
                    if hasattr(parent, 'data') and parent.data is not None and not parent.data.empty:
                        original_columns = list(parent.data.columns)
                        break
                # Continue walking up
                if hasattr(parent, 'parent'):
                    parent = parent.parent()
                else:
                    break
        except Exception:
            pass
        
        # Build ordered column list
        ordered_columns = []
        
        # 1. Add Pass/Row Index if it exists (first column)
        pass_col = None
        for col in df.columns:
            col_str = str(col).lower()
            if col_str in ['pass', 'row index']:
                pass_col = col
                ordered_columns.append(col)
                break
        
        # 2. Add all original data columns in their original order (if they exist in results)
        # This ensures ALL variables from original data are included
        if original_columns:
            for col in original_columns:
                # Include column if it exists in results and isn't already added
                if col in df.columns and col not in ordered_columns and col != '_composite_score':
                    ordered_columns.append(col)
        
        # 3. Add any columns in results that weren't in original data (shouldn't happen, but safety)
        for col in df.columns:
            if col not in ordered_columns and col != '_composite_score':
                ordered_columns.append(col)
        
        # 4. Add composite score at the end
        if '_composite_score' in df.columns:
            ordered_columns.append('_composite_score')
        
        # Return DataFrame with reordered columns (this should include ALL columns from df)
        return df[ordered_columns]
    
    def _create_results_table(self, df: pd.DataFrame) -> QTableWidget:
        """Create a table widget displaying optimization results."""
        table = QTableWidget()
        
        # Set dimensions
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        
        # Set headers
        table.setHorizontalHeaderLabels([str(col) for col in df.columns])
        
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
        
        # Populate data
        for row_idx, (idx, row) in enumerate(df.iterrows()):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val) if pd.notna(val) else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Align numeric columns to the right
                if pd.api.types.is_numeric_dtype(df.iloc[:, col_idx]):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                # Highlight composite score column
                if df.columns[col_idx] == '_composite_score':
                    item.setFont(QFont("", -1, QFont.Weight.Bold))
                
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
            QTableWidget::item:hover {
                background-color: #383838;
            }
        """)
        
        # Set row height
        table.verticalHeader().setVisible(False)
        for i in range(len(df)):
            table.setRowHeight(i, 40)
        
        # Resize columns to content
        table.resizeColumnsToContents()
        
        # Set minimum column widths
        for i in range(len(df.columns)):
            current_width = table.columnWidth(i)
            table.setColumnWidth(i, max(current_width, 100))
        
        return table
    
    def _on_back_clicked(self):
        """Handle back button click - return to configuration dialog."""
        if self.optimization_config and self.parent():
            # Get the data from parent (main window)
            from src.ui.main_window import MainWindow
            if isinstance(self.parent(), MainWindow):
                main_window = self.parent()
                if main_window.data is not None and not main_window.data.empty:
                    # Close this dialog
                    self.close()
                    
                    # Open configuration dialog with saved config
                    config_dialog = OptimizationDialog(
                        main_window.data, 
                        main_window, 
                        saved_config=self.optimization_config
                    )
                    
                    # Connect signal to handle optimization run without closing dialog
                    def on_run_optimization(config):
                        try:
                            # Run optimization again
                            from src.analysis.optimization import OptimizationAnalyzer
                            analyzer = OptimizationAnalyzer()
                            
                            result_data = analyzer.analyze(
                                data=main_window.data,
                                target_variables=config['target_variables'],
                                optimization_directions=config['optimization_directions'],
                                constraints=config['constraints'],
                                weights=config['weights'],
                                input_variables=config['input_variables'],
                                top_n=10
                            )
                            
                            # Add config to result_data for back button
                            result_data['config'] = config
                            
                            # Display new results (non-modal)
                            from src.ui.analysis_factory import AnalysisDialogFactory
                            result_dialog = AnalysisDialogFactory.create_dialog(
                                title="Optimization Results",
                                result_data=result_data,
                                result_type='optimization',
                                parent=config_dialog  # Parent to optimization dialog
                            )
                            result_dialog.show()  # Non-modal - doesn't block optimization dialog
                            
                        except Exception as e:
                            main_window._show_error(f"Error during optimization: {str(e)}")
                    
                    config_dialog.run_optimization.connect(on_run_optimization)
                    config_dialog.show()  # Show non-modal - doesn't block result dialog
    
    def _on_export_clicked(self):
        """Handle export to Excel button click."""
        if self.results_df is None or self.results_df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export.")
            return
        
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            "optimization_results.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Ensure .xlsx extension
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # Export DataFrame to Excel
            self.results_df.to_excel(file_path, index=False, engine='openpyxl')
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Results exported successfully to:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export to Excel:\n{str(e)}"
            )

