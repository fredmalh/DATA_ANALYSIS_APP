# Data Analysis Application

A modern, lightweight GUI application for data analysis with support for CSV, XLSX, and XML files.

## Features

- 📁 File upload/drag-and-drop support
- 📊 Tabular data display with column filters
- 🔍 Interactive data browsing
- 📈 Multiple data analysis tools
- 🎨 Modern, responsive UI

## Tech Stack

- **GUI Framework**: Flet (Flutter-based, cross-platform)
- **Data Processing**: pandas
- **File Support**: openpyxl (Excel), lxml (XML)
- **Visualization**: Plotly, Matplotlib

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Project Structure

```
DATA_ANALYSIS_APP/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── file_handler.py     # File loading and parsing
│   ├── data_processor.py   # Data manipulation utilities
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py  # Main application window
│   │   ├── data_table.py   # Table display component
│   │   └── analysis_dialogs.py  # Pop-up windows for results
│   └── analysis/
│       ├── __init__.py
│       └── analyzers.py    # Data analysis functions
└── requirements.txt
```

