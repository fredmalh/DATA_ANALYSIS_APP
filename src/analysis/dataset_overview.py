"""
Dataset Overview Analyzer Module
Analyzer for generating dataset overview statistics.
"""

from typing import Dict, Any
import pandas as pd
from src.analysis.base_analyzer import BaseAnalyzer


class DatasetOverviewAnalyzer(BaseAnalyzer):
    """Analyzer for generating dataset overview information."""
    
    def __init__(self):
        """Initialize the dataset overview analyzer."""
        super().__init__(
            name="Dataset Overview",
            description="Provides overview of dataset dimensions, data types, and missing values"
        )
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the dataset and generate overview statistics.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary containing:
            - 'success': bool
            - 'data': dict with dimensions, data_types, missing_values
            - 'summary': text summary
            - 'error': optional error message
        """
        # Validate data
        is_valid, error_msg = self.validate_data(data)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg,
                'data': {},
                'summary': None
            }
        
        try:
            # Calculate dimensions
            dimensions = {
                'rows': len(data),
                'columns': len(data.columns)
            }
            
            # Get data types
            data_types = {}
            for col in data.columns:
                dtype = str(data[col].dtype)
                data_types[col] = dtype
            
            # Calculate missing values percentage
            missing_values = {}
            total_rows = len(data)
            
            for col in data.columns:
                missing_count = data[col].isna().sum()
                missing_percent = (missing_count / total_rows * 100) if total_rows > 0 else 0
                missing_values[col] = {
                    'count': int(missing_count),
                    'percent': round(missing_percent, 2)
                }
            
            # Create summary text
            summary = (
                f"Dataset contains {dimensions['rows']} rows and {dimensions['columns']} columns. "
                f"Missing values range from {min([mv['percent'] for mv in missing_values.values()]):.2f}% "
                f"to {max([mv['percent'] for mv in missing_values.values()]):.2f}% per column."
            )
            
            return {
                'success': True,
                'data': {
                    'dimensions': dimensions,
                    'data_types': data_types,
                    'missing_values': missing_values
                },
                'summary': summary,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error analyzing dataset: {str(e)}",
                'data': {},
                'summary': None
            }
    
    def get_result_type(self) -> str:
        """Get the result type for this analyzer."""
        return 'dataset_overview'

