"""
Optimization Analyzer Module
Analyzer for finding optimal combinations of input variables to optimize target variables.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from src.analysis.base_analyzer import BaseAnalyzer


class OptimizationAnalyzer(BaseAnalyzer):
    """Analyzer for multi-objective optimization with constraints."""
    
    def __init__(self):
        """Initialize the optimization analyzer."""
        super().__init__(
            name="Optimization",
            description="Finds optimal combinations of input variables to optimize target variables with constraints"
        )
    
    def analyze(
        self, 
        data: pd.DataFrame,
        target_variables: List[str],
        optimization_directions: List[str],  # 'maximize' or 'minimize'
        constraints: Dict[int, Dict[str, Any]],  # {target_index: {'type': '>', 'value': 0}}
        weights: List[float],
        input_variables: List[str],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Perform optimization analysis.
        
        Args:
            data: DataFrame to analyze
            target_variables: List of 1-5 target variable names
            optimization_directions: List of 'maximize' or 'minimize' for each target
            constraints: Dictionary mapping target variable name to constraint dict
            weights: List of weights for each target (same length as target_variables)
            input_variables: List of input variable names
            top_n: Number of top solutions to return (default: 10)
            
        Returns:
            Dictionary containing:
            - 'success': bool
            - 'data': DataFrame with top N solutions
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
            # Validate inputs
            validation_error = self._validate_inputs(
                data, target_variables, optimization_directions, 
                constraints, weights, input_variables
            )
            if validation_error:
                return {
                    'success': False,
                    'error': validation_error,
                    'data': None,
                    'summary': None
                }
            
            # Ensure all lists have the same length (filtered to selected targets only)
            num_targets = len(target_variables)
            if len(optimization_directions) != num_targets:
                return {
                    'success': False,
                    'error': f"Mismatch: {num_targets} targets but {len(optimization_directions)} directions.",
                    'data': None,
                    'summary': None
                }
            if len(weights) != num_targets:
                return {
                    'success': False,
                    'error': f"Mismatch: {num_targets} targets but {len(weights)} weights.",
                    'data': None,
                    'summary': None
                }
            
            # Create working copy
            df = data.copy()
            
            # Filter by constraints
            df_filtered = self._apply_constraints(df, target_variables, constraints)
            
            if df_filtered.empty:
                return {
                    'success': False,
                    'error': "No rows satisfy the specified constraints.",
                    'data': None,
                    'summary': None
                }
            
            # Calculate composite scores
            scores = self._calculate_scores(
                df_filtered, target_variables, optimization_directions, weights
            )
            
            # Add score column
            df_filtered = df_filtered.copy()
            df_filtered['_composite_score'] = scores
            
            # Sort by score (descending - higher is better)
            df_sorted = df_filtered.sort_values('_composite_score', ascending=False)
            
            # Get top N solutions
            top_solutions = df_sorted.head(top_n).copy()
            
            # Select relevant columns for output
            output_columns = input_variables + target_variables + ['_composite_score']
            result_df = top_solutions[output_columns].copy()
            
            # Add row identifier: use "pass" column if it exists, otherwise use index
            if 'Pass' in data.columns:
                result_df.insert(0, 'Pass', top_solutions['Pass'].values)
            elif 'pass' in data.columns:
                result_df.insert(0, 'Pass', top_solutions['pass'].values)
            else:
                result_df.insert(0, 'Row Index', top_solutions.index)
            
            # Round numeric columns for display
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns
            result_df[numeric_cols] = result_df[numeric_cols].round(4)
            
            # Create summary
            summary = self._create_summary(
                len(data), len(df_filtered), len(result_df),
                target_variables, input_variables
            )
            
            return {
                'success': True,
                'data': result_df,
                'summary': summary,
                'error': None,
                'result_type': 'optimization'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error during optimization: {str(e)}",
                'data': None,
                'summary': None
            }
    
    def _validate_inputs(
        self,
        data: pd.DataFrame,
        target_variables: List[str],
        optimization_directions: List[str],
        constraints: Dict[str, Dict[str, Any]],  # Changed: now uses target name as key
        weights: List[float],
        input_variables: List[str]
    ) -> Optional[str]:
        """Validate optimization inputs."""
        # Check target variables (1-5 allowed)
        if len(target_variables) == 0:
            return "At least one target variable must be selected."
        
        if len(target_variables) > 5:
            return "Maximum 5 target variables allowed."
        
        for target in target_variables:
            if target not in data.columns:
                return f"Target variable '{target}' not found in data."
            if not pd.api.types.is_numeric_dtype(data[target]):
                return f"Target variable '{target}' must be numeric."
        
        # Check directions (must match number of targets)
        if len(optimization_directions) != len(target_variables):
            return f"Optimization direction must be specified for all {len(target_variables)} targets."
        
        for direction in optimization_directions:
            if direction not in ['maximize', 'minimize']:
                return f"Invalid optimization direction: {direction}. Must be 'maximize' or 'minimize'."
        
        # Check weights (must match number of targets)
        if len(weights) != len(target_variables):
            return f"Weights must be specified for all {len(target_variables)} targets."
        
        if any(w < 0 for w in weights):
            return "All weights must be non-negative."
        
        if sum(weights) == 0:
            return "At least one weight must be positive."
        
        # Validate constraint target names
        for target_name in constraints.keys():
            if target_name not in target_variables:
                return f"Constraint specified for '{target_name}' but this target is not selected."
        
        # Check input variables
        if len(input_variables) == 0:
            return "At least one input variable must be selected."
        
        for input_var in input_variables:
            if input_var not in data.columns:
                return f"Input variable '{input_var}' not found in data."
            if not pd.api.types.is_numeric_dtype(data[input_var]):
                return f"Input variable '{input_var}' must be numeric."
        
        # Check for overlap
        if set(target_variables) & set(input_variables):
            return "Target variables and input variables cannot overlap."
        
        return None
    
    def _apply_constraints(
        self,
        data: pd.DataFrame,
        target_variables: List[str],
        constraints: Dict[str, Dict[str, Any]]  # Changed: uses target name as key
    ) -> pd.DataFrame:
        """Apply constraints to filter data."""
        df = data.copy()
        
        # Apply constraints by target variable name
        for target_name, constraint in constraints.items():
            if target_name not in target_variables:
                continue  # Skip constraints for unselected targets
            
            constraint_type = constraint.get('type', '>')
            constraint_value = constraint.get('value', 0)
            
            if constraint_type == '>':
                df = df[df[target_name] > constraint_value]
            elif constraint_type == '>=':
                df = df[df[target_name] >= constraint_value]
            elif constraint_type == '<':
                df = df[df[target_name] < constraint_value]
            elif constraint_type == '<=':
                df = df[df[target_name] <= constraint_value]
            elif constraint_type == '==' or constraint_type == '=':
                df = df[df[target_name] == constraint_value]
        
        return df
    
    def _calculate_scores(
        self,
        data: pd.DataFrame,
        target_variables: List[str],
        optimization_directions: List[str],
        weights: List[float]
    ) -> np.ndarray:
        """Calculate composite scores for each row."""
        scores = np.zeros(len(data))
        
        for i, (target, direction, weight) in enumerate(zip(
            target_variables, optimization_directions, weights
        )):
            if weight == 0:
                continue
            
            # Get target values
            target_values = data[target].values
            
            # Normalize (min-max normalization)
            min_val = target_values.min()
            max_val = target_values.max()
            
            if max_val == min_val:
                # All values are the same, skip this target
                continue
            
            normalized = (target_values - min_val) / (max_val - min_val)
            
            # Apply direction: maximize = keep as is, minimize = invert
            if direction == 'minimize':
                normalized = 1 - normalized
            
            # Apply weight and add to score
            scores += weight * normalized
        
        # Normalize final scores to 0-1 range if needed
        if scores.max() > scores.min():
            scores = (scores - scores.min()) / (scores.max() - scores.min())
        
        return scores
    
    def _create_summary(
        self,
        total_rows: int,
        filtered_rows: int,
        result_rows: int,
        target_variables: List[str],
        input_variables: List[str]
    ) -> str:
        """Create summary text."""
        summary = f"Optimization Results:\n"
        summary += f"- Total rows in dataset: {total_rows}\n"
        summary += f"- Rows satisfying constraints: {filtered_rows}\n"
        summary += f"- Top solutions returned: {result_rows}\n"
        summary += f"- Target variables: {', '.join(target_variables)}\n"
        summary += f"- Input variables: {', '.join(input_variables)}"
        return summary
    
    def get_result_type(self) -> str:
        """Return the result type identifier."""
        return 'optimization'

