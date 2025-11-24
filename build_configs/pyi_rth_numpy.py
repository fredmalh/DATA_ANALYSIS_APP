"""
Runtime hook to fix numpy import issues in PyInstaller bundles.

This hook fixes the "you should not try to import numpy from its source directory" error
by patching the check in numpy's __init__.py that detects source directory imports.
"""

import sys
import os.path

# Fix for numpy import error in PyInstaller
# The error occurs because numpy checks if its __file__ is in a source directory
# by looking for setup.py in the parent directory of numpy/__init__.py

if hasattr(sys, '_MEIPASS'):
    # We're running from a PyInstaller bundle
    # Store original functions
    _original_exists = os.path.exists
    _original_isdir = os.path.isdir
    
    def _patched_exists(path):
        """Patched exists to prevent numpy source detection."""
        # If this is numpy checking for setup.py, return False
        # This prevents numpy from thinking it's in a source directory
        if isinstance(path, str) and 'numpy' in path.lower():
            if path.endswith('setup.py') or path.endswith(os.path.join('numpy', 'setup.py')):
                # Numpy is checking for setup.py - return False to indicate it's not a source tree
                return False
        return _original_exists(path)
    
    # Apply patches before numpy is imported
    os.path.exists = _patched_exists

