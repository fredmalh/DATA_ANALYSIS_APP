"""
Analysis Registry Module
Manages registration and retrieval of available analyzers.
"""

from typing import Dict, Type, Optional, List
from src.analysis.base_analyzer import BaseAnalyzer


class AnalysisRegistry:
    """Registry for managing available data analyzers."""
    
    _instance = None
    _analyzers: Dict[str, Type[BaseAnalyzer]] = {}
    
    def __new__(cls):
        """Singleton pattern - ensure only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, analyzer_id: str, analyzer_class: Type[BaseAnalyzer]):
        """
        Register an analyzer class.
        
        Args:
            analyzer_id: Unique identifier for the analyzer
            analyzer_class: Class that inherits from BaseAnalyzer
        """
        if not issubclass(analyzer_class, BaseAnalyzer):
            raise ValueError(f"Analyzer class must inherit from BaseAnalyzer")
        
        self._analyzers[analyzer_id] = analyzer_class
    
    def get_analyzer(self, analyzer_id: str) -> Optional[Type[BaseAnalyzer]]:
        """
        Get an analyzer class by ID.
        
        Args:
            analyzer_id: Identifier of the analyzer
            
        Returns:
            Analyzer class or None if not found
        """
        return self._analyzers.get(analyzer_id)
    
    def get_all_analyzers(self) -> Dict[str, Type[BaseAnalyzer]]:
        """
        Get all registered analyzers.
        
        Returns:
            Dictionary mapping analyzer IDs to analyzer classes
        """
        return self._analyzers.copy()
    
    def get_analyzer_ids(self) -> List[str]:
        """
        Get list of all registered analyzer IDs.
        
        Returns:
            List of analyzer ID strings
        """
        return list(self._analyzers.keys())
    
    def create_analyzer_instance(self, analyzer_id: str, *args, **kwargs) -> Optional[BaseAnalyzer]:
        """
        Create an instance of an analyzer.
        
        Args:
            analyzer_id: Identifier of the analyzer
            *args, **kwargs: Arguments to pass to analyzer constructor
            
        Returns:
            Analyzer instance or None if not found
        """
        analyzer_class = self.get_analyzer(analyzer_id)
        if analyzer_class:
            return analyzer_class(*args, **kwargs)
        return None


# Global registry instance
registry = AnalysisRegistry()

