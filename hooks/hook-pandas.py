"""
PyInstaller hook for pandas.

This hook ensures all pandas submodules and data files are collected properly.
Excludes test modules to avoid circular import issues.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Collect all pandas submodules, but exclude test modules
all_submodules = collect_submodules('pandas')
# Filter out test modules to avoid circular imports
# Keep pandas.testing as it's needed by pandas itself, but exclude pandas.tests.*
hiddenimports = [mod for mod in all_submodules if not mod.startswith('pandas.tests.')]

# Collect all pandas data files
datas = collect_data_files('pandas')

# Collect pandas dynamic libraries (DLLs on Windows)
binaries = collect_dynamic_libs('pandas')

