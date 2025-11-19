"""
File Handler Module
Handles loading and parsing of CSV, XLSX, and XML files.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple


class FileHandler:
    """Handles file loading and parsing for various data formats."""
    
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.xml'}
    
    @staticmethod
    def load_file(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Load a data file and return a DataFrame.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Tuple of (DataFrame, error_message)
            If successful: (DataFrame, None)
            If failed: (None, error_message)
        """
        path = Path(file_path)
        
        if not path.exists():
            return None, f"File not found: {file_path}"
        
        extension = path.suffix.lower()
        
        if extension not in FileHandler.SUPPORTED_EXTENSIONS:
            return None, f"Unsupported file type: {extension}"
        
        try:
            if extension == '.csv':
                df = pd.read_csv(file_path)
            elif extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif extension == '.xml':
                # Parse XML - try to find the actual table data, not just metadata
                df = FileHandler._load_xml_file(file_path)
            
            # Attempt to infer and convert data types automatically
            df = FileHandler._infer_data_types(df)
            
            return df, None
            
        except Exception as e:
            return None, f"Error loading file: {str(e)}"
    
    @staticmethod
    def _infer_data_types(df: pd.DataFrame) -> pd.DataFrame:
        """
        Attempt to infer and convert data types automatically.
        Converts object columns to numeric types where possible.
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with inferred data types
        """
        df = df.copy()
        
        for col in df.columns:
            # Skip if column is already numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            # Try to convert to numeric
            # First, try to convert the entire column
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            
            # Check if conversion was successful (not all NaN)
            if not numeric_series.isna().all():
                # Check if at least 80% of non-null values were successfully converted
                original_non_null = df[col].notna().sum()
                if original_non_null > 0:
                    converted_non_null = numeric_series.notna().sum()
                    conversion_rate = converted_non_null / original_non_null
                    
                    # If most values converted successfully, use numeric type
                    if conversion_rate >= 0.8:
                        df[col] = numeric_series
        
        return df
    
    @staticmethod
    def _load_xml_file(file_path: str) -> pd.DataFrame:
        """
        Load XML file, specifically targeting Excel XML format (SpreadsheetML).
        Structure: <Workbook><Worksheet><Table><Row>...</Row></Table></Worksheet></Workbook>
        Handles namespaces properly.
        """
        import xml.etree.ElementTree as ET
        
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Define namespaces used in Excel XML
        namespaces = {
            'ss': 'urn:schemas-microsoft-com:office:spreadsheet',
            '': 'urn:schemas-microsoft-com:office:spreadsheet'  # Default namespace
        }
        
        # Find the Table element (handle both with and without namespace prefix)
        table = None
        for ns_prefix, ns_url in namespaces.items():
            # Try with namespace prefix
            if ns_prefix:
                table = root.find(f'.//{{{ns_url}}}Table')
            else:
                # Try without prefix (default namespace)
                table = root.find('.//Table', namespaces)
            
            if table is not None:
                break
        
        # If still not found, try finding any Table element
        if table is None:
            for elem in root.iter():
                if 'Table' in elem.tag or elem.tag.endswith('}Table'):
                    table = elem
                    break
        
        if table is None:
            raise Exception("Could not find Table element in XML file")
        
        # Extract rows from the table
        rows = []
        for row_elem in table.findall('.//Row') or table.findall(f'.//{{{namespaces[""]}}}Row'):
            cells = []
            for cell_elem in row_elem.findall('.//Cell') or row_elem.findall(f'.//{{{namespaces[""]}}}Cell'):
                # Get the Data element inside the Cell
                data_elem = None
                for data in cell_elem.findall('.//Data') or cell_elem.findall(f'.//{{{namespaces[""]}}}Data'):
                    data_elem = data
                    break
                
                if data_elem is not None and data_elem.text is not None:
                    cells.append(data_elem.text.strip())
                else:
                    cells.append("")
            
            if cells:  # Only add non-empty rows
                rows.append(cells)
        
        if not rows:
            raise Exception("No data rows found in Table element")
        
        # First row is typically headers
        headers = rows[0]
        data_rows = rows[1:] if len(rows) > 1 else []
        
        # Create DataFrame
        if data_rows:
            # Ensure all rows have the same length as headers
            max_cols = len(headers)
            normalized_rows = []
            for row in data_rows:
                # Pad or truncate row to match header length
                normalized_row = row[:max_cols] + [""] * (max_cols - len(row))
                normalized_rows.append(normalized_row)
            
            df = pd.DataFrame(normalized_rows, columns=headers)
            return df
        else:
            # Only headers, no data
            df = pd.DataFrame(columns=headers)
            return df
    
    # @staticmethod
    # def is_supported_file(file_path: str) -> bool:
    #     """
    #     Check if file extension is supported.
    #     
    #     Note: Currently not used in the application, but kept as a utility method
    #     for potential future use (e.g., file validation before upload).
    #     """
    #     path = Path(file_path)
    #     return path.suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    # 
    # COMMENTED OUT: Method is defined but never called. May be useful for future
    # file validation features before upload.

