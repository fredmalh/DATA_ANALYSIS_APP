"""
PyInstaller hook for numpy.

This hook ensures all numpy submodules and data files are collected properly.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Collect all numpy submodules
hiddenimports = collect_submodules('numpy')

# Collect all numpy data files
datas = collect_data_files('numpy')

# Collect numpy dynamic libraries (DLLs on Windows)
binaries = collect_dynamic_libs('numpy')

