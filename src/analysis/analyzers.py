"""
Data Analysis Functions
Various data analysis operations that can be performed on the loaded dataset.
"""

import pandas as pd
from typing import Dict, Any


class DataAnalyzer:
    """Collection of data analysis functions."""
    
    @staticmethod
    def get_basic_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get basic statistical summary of the dataset.
        
        Returns:
            Dictionary containing statistics
        """
        stats = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else None,
        }
        return stats
    
    @staticmethod
    def format_statistics_text(stats: Dict[str, Any]) -> str:
        """Format statistics dictionary as readable text."""
        text = f"Dataset Shape: {stats['shape'][0]} rows × {stats['shape'][1]} columns\n\n"
        text += f"Columns: {', '.join(stats['columns'])}\n\n"
        
        if stats['missing_values']:
            text += "Missing Values:\n"
            for col, count in stats['missing_values'].items():
                if count > 0:
                    text += f"  - {col}: {count}\n"
            text += "\n"
        
        if stats['numeric_summary']:
            text += "Numeric Summary:\n"
            # Add numeric summary details here
            text += "  (Detailed statistics available)\n"
        
        return text

