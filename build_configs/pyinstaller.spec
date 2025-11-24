# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Data Analysis Application
"""

import os
from pathlib import Path

# Get the project root directory
# First try to get from environment variable (set by build script)
project_root = os.environ.get('PYINSTALLER_PROJECT_ROOT')
if project_root:
    project_root = Path(project_root)
else:
    # Fallback: Calculate from the spec file location
    # PyInstaller provides the spec file path in SPECPATH variable
    try:
        spec_file_path = SPECPATH
    except NameError:
        # Fallback: if SPECPATH is not available, use current working directory
        import sys
        if hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller bundle
            spec_file_path = os.path.abspath('pyinstaller.spec')
        else:
            spec_file_path = os.path.abspath('build_configs/pyinstaller.spec')
    
    spec_file_dir = os.path.dirname(os.path.abspath(spec_file_path))
    project_root = Path(spec_file_dir).parent

# Verify main.py exists
main_py_path = project_root / 'main.py'
if not main_py_path.exists():
    raise FileNotFoundError(f"main.py not found at {main_py_path}. Project root: {project_root}")

block_cipher = None

# Collect binaries - custom hook will handle numpy data files
try:
    import PyInstaller.utils.hooks as hooks
    # Collect numpy dynamic libraries (DLLs on Windows)
    numpy_binaries = hooks.collect_dynamic_libs('numpy')
    
    # Also collect pandas and matplotlib binaries if needed
    pandas_binaries = hooks.collect_dynamic_libs('pandas')
    matplotlib_binaries = hooks.collect_dynamic_libs('matplotlib')
    
    # Combine all binaries
    all_binaries = numpy_binaries + pandas_binaries + matplotlib_binaries
    # numpy_datas will be collected by the custom hook in hooks/hook-numpy.py
    numpy_datas = []
except Exception as e:
    # Fallback if hooks fail
    print(f"Warning: Could not collect some binaries: {e}")
    numpy_binaries = []
    numpy_datas = []
    all_binaries = []

# Exclude unnecessary modules to reduce size
# Be conservative - only exclude what we're absolutely sure isn't needed
excludes_list = [
    # Unused Python stdlib modules (but keep email, http, urllib as they're used by pkg_resources)
    'tkinter',
    'tkinter.*',
    'unittest',
    'test',
    'tests',
    'pydoc',
    'doctest',
    'pdb',
    'curses',
    # Unused matplotlib backends (we only need QtAgg)
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_gtk*',
    'matplotlib.backends.backend_wx*',
    'matplotlib.backends.backend_macosx',
    # Unused scipy modules (scipy is large, exclude unused parts)
    # Note: scipy might be pulled in by seaborn/pandas, but we can exclude unused submodules
    'scipy.sparse.csgraph',  # Only needed for some advanced features
    'scipy.optimize',  # Not used directly
    'scipy.integrate',  # Not used directly
    'scipy.signal',  # Not used directly
    'scipy.ndimage',  # Not used directly
    'scipy.spatial',  # Not used directly
    'scipy.interpolate',  # Not used directly
    'scipy.io',  # Not used directly
    # Don't exclude numpy modules - they're needed for proper package structure
    # Unused pandas modules
    'pandas.tests',  # Exclude test suite, but keep pandas.testing (needed by pandas)
    # Documentation and examples (be careful with this)
    # '*.example',  # Too aggressive, might break things
    # '*.examples',
]

a = Analysis(
    [str(project_root / 'main.py')],  # Use absolute path to main.py
    pathex=[str(project_root)],
    binaries=all_binaries if 'all_binaries' in locals() else numpy_binaries,  # Include all DLLs
    datas=numpy_datas,  # Include numpy data files
    hiddenimports=[
        # PyQt6 - only what we use
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        # Data processing - critical pandas and numpy imports
        'pandas',
        'pandas._config',
        'pandas._config.config',
        'pandas._config.localization',
        'pandas._config.dates',
        'pandas._libs',
        'pandas._libs.interval',
        'pandas._libs.hashtable',
        'pandas._libs.missing',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.base',
        'pandas._libs.tslibs.conversion',
        'pandas._libs.tslibs.offsets',
        'pandas._libs.tslibs.timestamps',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.fields',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.parsing',
        'pandas._libs.tslibs.period',
        'pandas._libs.tslibs.timezones',
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core.multiarray',  # Core array functionality
        'numpy.core.umath',  # Universal math functions
        'numpy.core._dtype_ctypes',  # Data type handling
        'numpy.linalg',
        'numpy.linalg.lapack_lite',
        'numpy.linalg._umath_linalg',
        'numpy.fft',
        'numpy.random',
        'numpy.random.mtrand',
        'numpy.random._generator',
        'numpy.random._pickle',
        'numpy.random._common',
        # Visualization - only Qt backend
        'matplotlib',
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_agg',  # Used by QtAgg
        'seaborn',
        # File handling
        'openpyxl',
        # PIL for matplotlib
        'PIL',
        'PIL.Image',
    ],
    hookspath=[str(project_root / 'hooks')],  # Use custom hooks directory
    hooksconfig={},
    runtime_hooks=[str(project_root / 'build_configs' / 'pyi_rth_numpy.py')],  # Fix numpy import
    excludes=excludes_list,  # Exclude unnecessary modules
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DataAnalysisApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Disable strip on Windows (strip tool not available, causes warnings)
    upx=True,  # Use UPX compression (if available)
    upx_exclude=[],  # Can exclude specific DLLs if UPX causes issues
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: 'path/to/icon.ico'
)

