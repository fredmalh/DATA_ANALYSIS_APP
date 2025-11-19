"""
2D Plot Dialog Module
Dialog for creating 2D scatter/line plots with variable selection.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from src.ui.analysis_dialogs import BaseAnalysisDialog

# Lazy import for matplotlib - only import when needed
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    Figure = None
    FigureCanvas = None
    NavigationToolbar = None
    plt = None


class Plot2DDialog(BaseAnalysisDialog):
    """Dialog for creating 2D plots with variable selection."""
    
    def __init__(self, title: str, result_data: Dict[str, Any], parent=None):
        """Initialize the 2D plot dialog."""
        # Set attributes before calling super().__init__() because _build_content() is called during initialization
        self.data = result_data.get('data')
        self.numeric_columns = result_data.get('numeric_columns', [])
        self.x_column = None
        self.y_column = None
        self.canvas = None
        self.ax = None
        
        # Now call super().__init__() which will call _build_content()
        super().__init__(title, result_data, parent)
        
        # Resize dialog for better plot viewing
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
    
    def _build_content(self) -> Optional[QWidget]:
        """Build content for 2D plot."""
        if not self.result_data.get('success', False):
            return super()._build_content()
        
        if not MATPLOTLIB_AVAILABLE:
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            error_widget.setLayout(error_layout)
            
            error_label = QLabel(
                "Matplotlib is not installed.\n\n"
                "Please install it by running:\n"
                "pip install matplotlib"
            )
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            
            return error_widget
        
        if len(self.numeric_columns) < 2:
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            error_widget.setLayout(error_layout)
            
            error_label = QLabel(
                "Need at least 2 numeric columns to create a 2D plot.\n\n"
                f"Found {len(self.numeric_columns)} numeric column(s)."
            )
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            
            return error_widget
        
        # Create main widget
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        main_widget.setLayout(layout)
        
        # Variable selection section
        selection_widget = self._create_selection_section()
        layout.addWidget(selection_widget)
        
        # Plot section
        plot_widget = self._create_plot_section()
        layout.addWidget(plot_widget)
        
        return main_widget
    
    def _create_selection_section(self) -> QWidget:
        """Create variable selection section."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        # X variable selection
        x_label = QLabel("X Variable:")
        x_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(x_label)
        
        self.x_combo = QComboBox()
        self.x_combo.addItems(self.numeric_columns)
        self.x_combo.setStyleSheet("""
            QComboBox {
                background-color: #303030;
                color: white;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #616161;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #303030;
                color: white;
                selection-background-color: #0d47a1;
            }
        """)
        self.x_combo.currentTextChanged.connect(self._on_variable_changed)
        layout.addWidget(self.x_combo)
        
        # Y variable selection
        y_label = QLabel("Y Variable:")
        y_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(y_label)
        
        self.y_combo = QComboBox()
        self.y_combo.addItems(self.numeric_columns)
        # Set different default if possible
        if len(self.numeric_columns) > 1:
            self.y_combo.setCurrentIndex(1)
        self.y_combo.setStyleSheet("""
            QComboBox {
                background-color: #303030;
                color: white;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #616161;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #303030;
                color: white;
                selection-background-color: #0d47a1;
            }
        """)
        self.y_combo.currentTextChanged.connect(self._on_variable_changed)
        layout.addWidget(self.y_combo)
        
        # Swap button
        swap_button = QPushButton("Swap X ↔ Y")
        swap_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 5px;
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
        swap_button.clicked.connect(self._swap_variables)
        layout.addWidget(swap_button)
        
        layout.addStretch()
        
        return widget
    
    def _create_plot_section(self) -> QWidget:
        """Create the plot section with matplotlib."""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 7), facecolor='#212121')
        self.canvas = FigureCanvas(fig)
        self.ax = fig.add_subplot(111, facecolor='#212121')
        
        # Set dark theme
        plt.style.use('dark_background')
        
        # Add navigation toolbar
        toolbar = NavigationToolbar(self.canvas, container)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #303030;
                border: none;
                padding: 5px;
            }
            QToolButton {
                background-color: #424242;
                color: white;
                border: 1px solid #616161;
                border-radius: 3px;
                padding: 5px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #616161;
            }
        """)
        layout.addWidget(toolbar)
        
        # Add canvas
        layout.addWidget(self.canvas)
        
        # Initial plot
        self._update_plot()
        
        return container
    
    def _on_variable_changed(self):
        """Handle variable selection change."""
        self._update_plot()
    
    def _swap_variables(self):
        """Swap X and Y variables."""
        current_x = self.x_combo.currentText()
        current_y = self.y_combo.currentText()
        
        # Swap in comboboxes
        x_index = self.x_combo.findText(current_y)
        y_index = self.y_combo.findText(current_x)
        
        if x_index >= 0:
            self.x_combo.setCurrentIndex(x_index)
        if y_index >= 0:
            self.y_combo.setCurrentIndex(y_index)
        
        # Plot will update automatically via signal
    
    def _update_plot(self):
        """Update the plot with current variable selections."""
        if self.ax is None or self.canvas is None:
            return
        
        x_var = self.x_combo.currentText()
        y_var = self.y_combo.currentText()
        
        if not x_var or not y_var:
            return
        
        # Clear previous plot
        self.ax.clear()
        
        # Get data
        x_data = self.data[x_var].dropna()
        y_data = self.data[y_var].dropna()
        
        # Align indices (in case of different missing values)
        common_idx = x_data.index.intersection(y_data.index)
        x_plot = x_data.loc[common_idx]
        y_plot = y_data.loc[common_idx]
        
        if len(x_plot) == 0 or len(y_plot) == 0:
            self.ax.text(0.5, 0.5, 'No data to plot', 
                        transform=self.ax.transAxes,
                        ha='center', va='center',
                        color='white', fontsize=14)
            self.canvas.draw()
            return
        
        # Create scatter plot
        self.ax.scatter(x_plot, y_plot, alpha=0.6, s=30, color='#64B5F6', edgecolors='#1976D2', linewidths=0.5)
        
        # Set labels
        self.ax.set_xlabel(x_var, color='white', fontsize=11, fontweight='bold')
        self.ax.set_ylabel(y_var, color='white', fontsize=11, fontweight='bold')
        
        # Set title
        self.ax.set_title(f'{y_var} vs {x_var}', color='white', fontsize=13, fontweight='bold', pad=15)
        
        # Style axes
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('#616161')
        self.ax.spines['top'].set_color('#616161')
        self.ax.spines['right'].set_color('#616161')
        self.ax.spines['left'].set_color('#616161')
        self.ax.grid(True, alpha=0.3, color='#424242', linestyle='--')
        
        # Refresh canvas
        self.canvas.draw()

