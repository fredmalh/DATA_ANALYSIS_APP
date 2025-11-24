"""
Build script for PyInstaller
Creates an executable using PyInstaller with the configured spec file.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_build_dirs():
    """Get build directory paths."""
    build_dir = project_root / 'build' / 'pyinstaller'
    dist_dir = build_dir / 'dist'
    build_temp_dir = build_dir / 'build'
    return build_dir, dist_dir, build_temp_dir

def clean_build():
    """Clean previous build artifacts."""
    import shutil
    import stat
    
    build_dir, dist_dir, build_temp_dir = get_build_dirs()
    
    print("Cleaning previous PyInstaller build...")
    
    # Clean dist directory - handle locked files on Windows
    if dist_dir.exists():
        try:
            # Try to remove read-only attributes and delete files
            for item in dist_dir.rglob('*'):
                try:
                    if item.is_file():
                        item.chmod(stat.S_IWRITE)  # Remove read-only
                        item.unlink()
                    elif item.is_dir():
                        try:
                            item.chmod(stat.S_IWRITE)
                            item.rmdir()
                        except OSError:
                            pass  # Directory not empty, will be handled by rmtree
                except (PermissionError, OSError):
                    pass  # Skip locked files
            
            # Try to remove the directory
            try:
                shutil.rmtree(dist_dir)
                print(f"  Removed: {dist_dir}")
            except PermissionError:
                print(f"  Warning: Could not remove {dist_dir} (executable might be in use)")
                print("  Continuing anyway - PyInstaller will overwrite...")
        except Exception as e:
            print(f"  Warning: Error cleaning {dist_dir}: {e}")
            print("  Continuing anyway...")
    
    # Clean build directory
    if build_temp_dir.exists():
        try:
            shutil.rmtree(build_temp_dir)
            print(f"  Removed: {build_temp_dir}")
        except Exception as e:
            print(f"  Warning: Could not remove {build_temp_dir}: {e}")

def build_executable(clean=True):
    """Build executable using PyInstaller."""
    spec_file = project_root / 'build_configs' / 'pyinstaller.spec'
    
    if not spec_file.exists():
        print(f"Error: Spec file not found at {spec_file}")
        return False
    
    if clean:
        clean_build()
    
    print("\n" + "="*60)
    print("Building with PyInstaller...")
    print("="*60)
    print(f"Spec file: {spec_file}")
    print(f"Output directory: {project_root / 'build' / 'pyinstaller' / 'dist'}")
    print()
    
    start_time = time.time()
    
    try:
        # Run PyInstaller with project root as environment variable
        env = os.environ.copy()
        env['PYINSTALLER_PROJECT_ROOT'] = str(project_root)
        
        # Set output directories
        dist_dir = project_root / 'build' / 'pyinstaller' / 'dist'
        work_dir = project_root / 'build' / 'pyinstaller' / 'build'
        dist_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Run PyInstaller with explicit distpath and workpath
        # Add optimization flags for faster builds and smaller executables
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--distpath', str(dist_dir),
            '--workpath', str(work_dir),
            '--log-level=WARN',  # Reduce log verbosity for faster output
            str(spec_file)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            env=env,
            check=True,
            capture_output=False
        )
        
        build_time = time.time() - start_time
        
        # Check both possible locations (spec might output to default dist/ or custom location)
        dist_dir_custom = project_root / 'build' / 'pyinstaller' / 'dist'
        dist_dir_default = project_root / 'dist'
        
        # Try custom location first, then default
        if (dist_dir_custom / 'DataAnalysisApp.exe').exists():
            exe_path = dist_dir_custom / 'DataAnalysisApp.exe'
        elif (dist_dir_default / 'DataAnalysisApp.exe').exists():
            exe_path = dist_dir_default / 'DataAnalysisApp.exe'
            # Move it to the expected location
            dist_dir_custom.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.move(str(exe_path), str(dist_dir_custom / 'DataAnalysisApp.exe'))
            exe_path = dist_dir_custom / 'DataAnalysisApp.exe'
        else:
            exe_path = None
        
        if exe_path and exe_path.exists():
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
    parser = argparse.ArgumentParser(description='Build executable with PyInstaller')
    parser.add_argument('--no-clean', action='store_true', help='Skip cleaning previous build')
    args = parser.parse_args()
    
    success, result = build_executable(clean=not args.no_clean)
    sys.exit(0 if success else 1)

