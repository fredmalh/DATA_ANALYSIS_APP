"""
Basic Statistics Analyzer Module
Analyzer for computing basic descriptive statistics for each variable.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from src.analysis.base_analyzer import BaseAnalyzer


class BasicStatisticsAnalyzer(BaseAnalyzer):
    """Analyzer for computing basic descriptive statistics."""
    
    def __init__(self):
        """Initialize the basic statistics analyzer."""
        super().__init__(
            name="Basic Statistics",
            description="Computes mean, quartiles, min, max, skewness, kurtosis, and cardinality for each variable"
        )
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the dataset and compute basic statistics for each variable.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary containing:
            - 'success': bool
            - 'data': dict with statistics for each column
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
            statistics = {}
            constant_vars = []
            near_constant_vars = []
            
            for col in data.columns:
                col_stats = {}
                
                # Check if column is numeric
                if pd.api.types.is_numeric_dtype(data[col]):
                    col_data = data[col].dropna()
                    
                    if len(col_data) > 0:
                        # Basic statistics
                        col_stats['mean'] = float(col_data.mean())
                        col_stats['min'] = float(col_data.min())
                        col_stats['q1'] = float(col_data.quantile(0.25))
                        col_stats['median'] = float(col_data.median())
                        col_stats['q3'] = float(col_data.quantile(0.75))
                        col_stats['max'] = float(col_data.max())
                        
                        # Skewness
                        if len(col_data) > 2:
                            col_stats['skewness'] = float(col_data.skew())
                        else:
                            col_stats['skewness'] = None
                        
                        # Kurtosis
                        if len(col_data) > 3:
                            col_stats['kurtosis'] = float(col_data.kurtosis())
                        else:
                            col_stats['kurtosis'] = None
                        
                        # Cardinality (number of unique values)
                        col_stats['cardinality'] = int(col_data.nunique())
                        
                        # Check for constant or near-constant variables
                        unique_ratio = col_stats['cardinality'] / len(col_data) if len(col_data) > 0 else 0
                        
                        if col_stats['cardinality'] == 1:
                            col_stats['is_constant'] = True
                            col_stats['is_near_constant'] = False
                            constant_vars.append(col)
                        elif unique_ratio < 0.01:  # Less than 1% unique values
                            col_stats['is_constant'] = False
                            col_stats['is_near_constant'] = True
                            near_constant_vars.append(col)
                        else:
                            col_stats['is_constant'] = False
                            col_stats['is_near_constant'] = False
                    else:
                        # All values are NaN
                        col_stats = {
                            'mean': None, 'min': None, 'q1': None, 'median': None,
                            'q3': None, 'max': None, 'skewness': None, 'kurtosis': None,
                            'cardinality': 0, 'is_constant': False, 'is_near_constant': False
                        }
                else:
                    # Non-numeric column - only compute cardinality
                    col_stats['mean'] = None
                    col_stats['min'] = None
                    col_stats['q1'] = None
                    col_stats['median'] = None
                    col_stats['q3'] = None
                    col_stats['max'] = None
                    col_stats['skewness'] = None
                    col_stats['kurtosis'] = None
                    col_stats['cardinality'] = int(data[col].nunique())
                    
                    # Check for constant or near-constant
                    unique_ratio = col_stats['cardinality'] / len(data[col]) if len(data[col]) > 0 else 0
                    
                    if col_stats['cardinality'] == 1:
                        col_stats['is_constant'] = True
                        col_stats['is_near_constant'] = False
                        constant_vars.append(col)
                    elif unique_ratio < 0.01:
                        col_stats['is_constant'] = False
                        col_stats['is_near_constant'] = True
                        near_constant_vars.append(col)
                    else:
                        col_stats['is_constant'] = False
                        col_stats['is_near_constant'] = False
                
                statistics[col] = col_stats
            
            # Create summary
            summary_parts = []
            if constant_vars:
                summary_parts.append(f"{len(constant_vars)} constant variable(s)")
            if near_constant_vars:
                summary_parts.append(f"{len(near_constant_vars)} near-constant variable(s)")
            if not summary_parts:
                summary_parts.append("No constant or near-constant variables detected")
            
            summary = f"Statistics computed for {len(data.columns)} variables. " + ", ".join(summary_parts) + "."
            
            return {
                'success': True,
                'data': statistics,
                'summary': summary,
                'constant_vars': constant_vars,
                'near_constant_vars': near_constant_vars,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error computing statistics: {str(e)}",
                'data': {},
                'summary': None
            }
    
    def get_result_type(self) -> str:
        """Get the result type for this analyzer."""
        return 'basic_statistics'

