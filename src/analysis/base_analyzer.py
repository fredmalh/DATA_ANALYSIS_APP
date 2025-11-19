"""
Base Analyzer Module
Abstract base class defining the interface for all data analyzers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class BaseAnalyzer(ABC):
    """Abstract base class for all data analyzers."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the analyzer.
        
        Args:
            name: Display name of the analyzer
            description: Description of what the analyzer does
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform the analysis on the provided data.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary containing analysis results. Should include:
            - 'success': bool indicating if analysis succeeded
            - 'data': the actual results (structure depends on analyzer type)
            - 'error': optional error message if success is False
            - 'summary': optional text summary of results
        """
        pass
    
    @abstractmethod
    def get_result_type(self) -> str:
        """
        Get the type of result this analyzer produces.
        Used to determine which dialog/view to use for display.
        
        Returns:
            String identifier for the result type (e.g., 'statistics', 'correlation', 'chart')
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> tuple[bool, Optional[str]]:
        """
        Validate that the data is suitable for this analysis.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, error_message)
        """
        if data is None:
            return False, "No data provided"
        
        if data.empty:
            return False, "DataFrame is empty"
        
        return True, None
    
    def get_name(self) -> str:
        """Get the display name of this analyzer."""
        return self.name
    
    def get_description(self) -> str:
        """Get the description of this analyzer."""
        return self.description

