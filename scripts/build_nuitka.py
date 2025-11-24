"""
Build script for Nuitka
Creates an executable using Nuitka.
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_build_dirs():
    """Get build directory paths."""
    build_dir = project_root / 'build' / 'nuitka'
    dist_dir = build_dir / 'dist'
    build_temp_dir = build_dir / 'build'
    return build_dir, dist_dir, build_temp_dir

def clean_build():
    """Clean previous build artifacts."""
    build_dir, dist_dir, build_temp_dir = get_build_dirs()
    
    print("Cleaning previous Nuitka build...")
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
        print(f"  Removed: {dist_dir}")
    if build_temp_dir.exists():
        import shutil
        shutil.rmtree(build_temp_dir)
        print(f"  Removed: {build_temp_dir}")
    
    # Remove .build directory if exists
    build_cache = project_root / 'DataAnalysisApp.build'
    if build_cache.exists():
        import shutil
        shutil.rmtree(build_cache)
        print(f"  Removed: {build_cache}")
    
    # Remove .dist directory if exists
    dist_cache = project_root / 'DataAnalysisApp.dist'
    if dist_cache.exists():
        import shutil
        shutil.rmtree(dist_cache)
        print(f"  Removed: {dist_cache}")

def find_vcvarsall():
    """Find vcvarsall.bat which sets up MSVC environment."""
    # Common Visual Studio installation paths
    vs_paths = [
        r"C:\Program Files\Microsoft Visual Studio",
        r"C:\Program Files (x86)\Microsoft Visual Studio",
    ]
    
    # Look for vcvarsall.bat in common locations
    for vs_path in vs_paths:
        if os.path.exists(vs_path):
            # Check for different VS versions (2022, 2019, etc.)
            for year in ['2022', '2019', '2017']:
                for edition in ['Enterprise', 'Professional', 'Community', 'BuildTools']:
                    vcvars_path = Path(vs_path) / year / edition / 'VC' / 'Auxiliary' / 'Build' / 'vcvarsall.bat'
                    if vcvars_path.exists():
                        return str(vcvars_path)
    
    return None

def check_msvc_available():
    """Check if MSVC compiler is available and accessible."""
    # Check for cl.exe in PATH (most reliable check)
    if shutil.which('cl.exe'):
        return True, True  # Available and in PATH
    
    # Check if vcvarsall.bat exists (VS installed but not in PATH)
    vcvars = find_vcvarsall()
    if vcvars:
        return True, False  # Available but needs environment setup
    
    return False, False  # Not available

def build_executable(clean=True):
    """Build executable using Nuitka."""
    main_file = project_root / 'main.py'
    
    if not main_file.exists():
        print(f"Error: Main file not found at {main_file}")
        return False
    
    if clean:
        clean_build()
    
    print("\n" + "="*60)
    print("Building with Nuitka...")
    print("="*60)
    print(f"Main file: {main_file}")
    print(f"Output directory: {project_root / 'build' / 'nuitka' / 'dist'}")
    print()
    
    # Check if Nuitka is installed
    try:
        import nuitka
    except ImportError:
        print("\n✗ Nuitka is not installed!")
        print("Please install it with: pip install nuitka")
        return False, {
            'success': False,
            'error': 'Nuitka module not found. Install with: pip install nuitka',
            'build_time': 0
        }
    
    # Check Python version for compiler selection
    python_version = sys.version_info
    use_msvc = python_version >= (3, 13)  # Python 3.13+ requires MSVC
    
        if use_msvc:
            print("Note: Python 3.13 detected. MSVC compiler is required.")
            msvc_installed, msvc_in_path = check_msvc_available()
            if not msvc_installed:
                print("⚠ Warning: MSVC compiler not detected.")
                print("   The build will fail. You have two options:")
                print("   1. Install Visual Studio Build Tools (recommended)")
                print("      - Download from: https://visualstudio.microsoft.com/downloads/")
                print("      - Select 'Build Tools for Visual Studio'")
                print("      - Install 'Desktop development with C++' workload")
                print("      - Run this script from 'Developer Command Prompt for VS'")
                print("   2. Use PyInstaller instead: python scripts/build_pyinstaller.py")
                print()
            elif not msvc_in_path:
                print("⚠ Warning: Visual Studio is installed but compiler is not in PATH.")
                print("   The build may fail. Please run this script from:")
                print("   'Developer Command Prompt for Visual Studio'")
                print("   (Found in Start Menu under Visual Studio folder)")
                print()
                print("   Alternatively, you can use PyInstaller which doesn't require this:")
                print("   python scripts/build_pyinstaller.py")
                print()
            else:
                print("✓ MSVC compiler detected and available in PATH.")
                print()
    
    start_time = time.time()
    
    try:
        # Prepare Nuitka command
        cmd = [
            sys.executable, '-m', 'nuitka',
            '--standalone',
            '--onefile',
            '--windows-console-mode=disable',  # No console window (updated flag)
            '--enable-plugin=pyqt6',
            '--include-module=pandas',
            '--include-module=numpy',
            '--include-module=matplotlib',
            '--include-module=seaborn',
            '--include-module=openpyxl',
            '--include-module=scipy',
            '--include-package-data=pandas',
            '--include-package-data=matplotlib',
            '--output-dir=' + str(project_root / 'build' / 'nuitka' / 'dist'),
            '--output-filename=DataAnalysisApp.exe',
            str(main_file)
        ]
        
        # Add compiler option based on Python version
        if use_msvc:
            cmd.insert(4, '--msvc=latest')  # Insert after --onefile
        else:
            cmd.insert(4, '--mingw64')  # Use MinGW64 for Python < 3.13
        
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            check=True,
            capture_output=False
        )
        
        build_time = time.time() - start_time
        
        dist_dir = project_root / 'build' / 'nuitka' / 'dist'
        exe_path = dist_dir / 'DataAnalysisApp.exe'
        
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print("\n" + "="*60)
            print("✓ Build successful!")
            print("="*60)
            print(f"Executable: {exe_path}")
            print(f"Size: {file_size:.2f} MB")
            print(f"Build time: {build_time:.2f} seconds")
            return True, {
                'success': True,
                'exe_path': str(exe_path),
                'size_mb': file_size,
                'build_time': build_time
            }
        else:
            print("\n✗ Build completed but executable not found!")
            return False, {
                'success': False,
                'error': 'Executable not found after build'
            }
            
    except subprocess.CalledProcessError as e:
        build_time = time.time() - start_time
        print(f"\n✗ Build failed after {build_time:.2f} seconds")
        print(f"Error: {e}")
        
        # Provide helpful error message for compiler issues
        if use_msvc:
            print("\n" + "="*60)
            print("MSVC Compiler Not Found")
            print("="*60)
            print("Python 3.13 requires MSVC compiler for Nuitka builds.")
            print("\nTo fix this, you have two options:")
            print("\n1. Install Visual Studio Build Tools:")
            print("   - Download from: https://visualstudio.microsoft.com/downloads/")
            print("   - Select 'Build Tools for Visual Studio'")
            print("   - Install 'Desktop development with C++' workload")
            print("\n2. Use PyInstaller instead (already working):")
            print("   python scripts/build_pyinstaller.py")
            print("="*60)
        
        return False, {
            'success': False,
            'error': str(e),
            'build_time': build_time
        }
    except Exception as e:
        build_time = time.time() - start_time
        print(f"\n✗ Unexpected error: {e}")
        return False, {
            'success': False,
            'error': str(e),
            'build_time': build_time
        }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Build executable with Nuitka')
    parser.add_argument('--no-clean', action='store_true', help='Skip cleaning previous build')
    args = parser.parse_args()
    
    success, result = build_executable(clean=not args.no_clean)
    sys.exit(0 if success else 1)

