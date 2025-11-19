"""
Analysis Factory Module
Factory for creating appropriate result dialogs based on analysis results.
"""

from typing import Dict, Any, Optional
from src.ui.analysis_dialogs import (
    BaseAnalysisDialog, StatisticsResultDialog, TextResultDialog
)
from src.ui.dataset_overview_dialog import DatasetOverviewDialog
from src.ui.basic_statistics_dialog import BasicStatisticsDialog
from src.ui.correlation_dialog import CorrelationDialog
from src.ui.optimization_result_dialog import OptimizationResultDialog


class AnalysisDialogFactory:
    """Factory for creating analysis result dialogs."""
    
    # Map result types to dialog classes
    _dialog_map = {
        'statistics': StatisticsResultDialog,
        'text': TextResultDialog,
        'table': StatisticsResultDialog,  # Can reuse statistics dialog for tables
        'dataset_overview': DatasetOverviewDialog,
        'basic_statistics': BasicStatisticsDialog,
        'correlation': CorrelationDialog,
        'optimization': OptimizationResultDialog,
    }
    
    @classmethod
    def create_dialog(
        cls, 
        title: str, 
        result_data: Dict[str, Any], 
        result_type: Optional[str] = None,
        parent=None
    ) -> BaseAnalysisDialog:
        """
        Create an appropriate dialog for displaying analysis results.
        
        Args:
            title: Dialog window title
            result_data: Dictionary containing analysis results
            result_type: Type of result (if None, will try to infer from result_data)
            parent: Parent window
            
        Returns:
            BaseAnalysisDialog instance
        """
        # If result_type not provided, try to infer it
        if result_type is None:
            result_type = result_data.get('result_type', 'text')
        
        # Get dialog class from map, default to base dialog
        dialog_class = cls._dialog_map.get(result_type, BaseAnalysisDialog)
        
        # Create and return dialog instance
        # For optimization, pass config if available
        if result_type == 'optimization' and 'config' in result_data:
            return dialog_class(title, result_data, parent, config=result_data.get('config'))
        return dialog_class(title, result_data, parent)
    
    @classmethod
    def register_dialog_type(cls, result_type: str, dialog_class: type):
        """
        Register a new dialog type for a result type.
        
        Args:
            result_type: String identifier for the result type
            dialog_class: Class that inherits from BaseAnalysisDialog
        """
        if not issubclass(dialog_class, BaseAnalysisDialog):
            raise ValueError(f"Dialog class must inherit from BaseAnalysisDialog")
        
        cls._dialog_map[result_type] = dialog_class

