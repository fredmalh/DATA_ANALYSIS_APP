"""
Correlation Dialog Module
Dialog for displaying correlation heatmap.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from src.ui.analysis_dialogs import BaseAnalysisDialog

# Lazy import for matplotlib and seaborn - only import when needed
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
    SEABORN_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    SEABORN_AVAILABLE = False
    Figure = None
    FigureCanvas = None
    NavigationToolbar = None
    plt = None
    sns = None


class CorrelationDialog(BaseAnalysisDialog):
    """Dialog for displaying correlation heatmap."""
    
    def _build_content(self) -> QWidget:
        """Build content for correlation results."""
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
        
        correlation_matrix = self.result_data.get('data')
        numeric_columns = self.result_data.get('numeric_columns', [])
        
        if correlation_matrix is not None and len(numeric_columns) > 0:
            # Create heatmap
            heatmap_widget = self._create_heatmap(correlation_matrix, numeric_columns)
            content_layout.addWidget(heatmap_widget)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    def _create_heatmap(self, correlation_matrix: pd.DataFrame, columns: list) -> QWidget:
        """Create a beautiful correlation heatmap using seaborn."""
        # Check if matplotlib and seaborn are available
        if not MATPLOTLIB_AVAILABLE:
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            error_widget.setLayout(error_layout)
            
            error_label = QLabel(
                "Matplotlib is not installed.\n\n"
                "Please install it by running:\n"
                "pip install matplotlib seaborn"
            )
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            
            return error_widget
        
        if not SEABORN_AVAILABLE:
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            error_widget.setLayout(error_layout)
            
            error_label = QLabel(
                "Seaborn is not installed.\n\n"
                "Please install it by running:\n"
                "pip install seaborn"
            )
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            
            return error_widget
        
        # Create matplotlib figure with dark theme
        fig = Figure(figsize=(10, 8), facecolor='#212121')
        canvas = FigureCanvas(fig)
        
        # Set matplotlib to use dark background
        plt.style.use('dark_background')
        sns.set_style("dark")
        
        ax = fig.add_subplot(111, facecolor='#212121')
        
        # Create heatmap using seaborn
        sns.heatmap(correlation_matrix, cmap="crest", annot=True, fmt=".1f",
                   ax=ax, cbar_kws={'label': 'Correlation'}, 
                   xticklabels=columns, yticklabels=columns,
                   linewidths=0.5, linecolor='#424242')
        
        # Style the labels
        ax.set_xticklabels(columns, rotation=45, ha='right', color='white', fontsize=9)
        ax.set_yticklabels(columns, color='white', fontsize=9)
        
        # Style the colorbar (seaborn creates it automatically)
        # Get colorbar from the figure
        if ax.collections:
            cbar = ax.collections[0].colorbar
            if cbar:
                cbar.ax.tick_params(colors='white')
                cbar.set_label('Correlation', color='white', fontsize=10, rotation=270, labelpad=20)
        
        # Set title
        ax.set_title('Correlation Matrix Heatmap', color='white', fontsize=14, fontweight='bold', pad=20)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create container widget
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar(canvas, container)
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
        layout.addWidget(canvas)
        
        return container

