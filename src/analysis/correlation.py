"""
Correlation Analyzer Module
Analyzer for computing correlation matrix between numeric variables.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from src.analysis.base_analyzer import BaseAnalyzer


class CorrelationAnalyzer(BaseAnalyzer):
    """Analyzer for computing correlation matrix."""
    
    def __init__(self):
        """Initialize the correlation analyzer."""
        super().__init__(
            name="Correlation Analysis",
            description="Computes correlation matrix between numeric variables and displays as heatmap"
        )
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the dataset and compute correlation matrix.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary containing:
            - 'success': bool
            - 'data': correlation matrix as DataFrame
            - 'summary': text summary
            - 'error': optional error message
        """
        # Validate data
        is_valid, error_msg = self.validate_data(data)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg,
                'data': None,
                'summary': None
            }
        
        try:
            # Select only numeric columns
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) < 2:
                return {
                    'success': False,
                    'error': "Need at least 2 numeric columns to compute correlations.",
                    'data': None,
                    'summary': None
                }
            
            # Compute correlation matrix
            correlation_matrix = data[numeric_cols].corr()
            
            # Create summary
            summary = (
                f"Correlation matrix computed for {len(numeric_cols)} numeric variables. "
                f"Values range from {correlation_matrix.min().min():.3f} to {correlation_matrix.max().max():.3f}."
            )
            
            return {
                'success': True,
                'data': correlation_matrix,
                'numeric_columns': numeric_cols,
                'summary': summary,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error computing correlations: {str(e)}",
                'data': None,
                'summary': None
            }
    
    def get_result_type(self) -> str:
        """Get the result type for this analyzer."""
        return 'correlation'

