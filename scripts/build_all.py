"""
Build script that runs both PyInstaller and Nuitka, then generates a comparison report.
"""

import sys
import time 
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import build functions directly
import importlib.util

def load_build_function(script_name):
    """Load a build function from a script file."""
    script_path = project_root / 'scripts' / f'{script_name}.py'
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_executable

# Load build functions
build_pyinstaller = load_build_function('build_pyinstaller')
build_nuitka = load_build_function('build_nuitka')

def get_directory_size(path):
    """Calculate total size of a directory in MB."""
    if not path.exists():
        return 0
    
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total / (1024 * 1024)

def generate_markdown_report(results, output_path):
    """Generate a Markdown comparison report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Helper function to format size
    def format_size(size):
        if isinstance(size, (int, float)):
            return f"{size:.2f}"
        return str(size)
    
    pyinstaller_size = format_size(results['pyinstaller'].get('size_mb', 'N/A'))
    nuitka_size = format_size(results['nuitka'].get('size_mb', 'N/A'))
    
    report = f"""# Build Comparison Report

**Generated:** {timestamp}

## Summary

| Tool | Status | Executable Size | Build Time |
|------|--------|-----------------|------------|
| PyInstaller | {'✓ Success' if results['pyinstaller']['success'] else '✗ Failed'} | {pyinstaller_size} MB | {results['pyinstaller'].get('build_time', 0):.2f}s |
| Nuitka | {'✓ Success' if results['nuitka']['success'] else '✗ Failed'} | {nuitka_size} MB | {results['nuitka'].get('build_time', 0):.2f}s |

## Detailed Results

### PyInstaller

"""
    
    if results['pyinstaller']['success']:
        report += f"""
- **Status:** ✓ Build Successful
- **Executable Path:** `{results['pyinstaller']['exe_path']}`
- **File Size:** {results['pyinstaller']['size_mb']:.2f} MB
- **Build Time:** {results['pyinstaller']['build_time']:.2f} seconds
"""
    else:
        report += f"""
- **Status:** ✗ Build Failed
- **Error:** {results['pyinstaller'].get('error', 'Unknown error')}
- **Build Time:** {results['pyinstaller'].get('build_time', 0):.2f} seconds
"""
    
    report += "\n### Nuitka\n\n"
    
    if results['nuitka']['success']:
        report += f"""
- **Status:** ✓ Build Successful
- **Executable Path:** `{results['nuitka']['exe_path']}`
- **File Size:** {results['nuitka']['size_mb']:.2f} MB
- **Build Time:** {results['nuitka']['build_time']:.2f} seconds
"""
    else:
        report += f"""
- **Status:** ✗ Build Failed
- **Error:** {results['nuitka'].get('error', 'Unknown error')}
- **Build Time:** {results['nuitka'].get('build_time', 0):.2f} seconds
"""
    
    # Add comparison section if both succeeded
    if results['pyinstaller']['success'] and results['nuitka']['success']:
        size_diff = results['pyinstaller']['size_mb'] - results['nuitka']['size_mb']
        time_diff = results['pyinstaller']['build_time'] - results['nuitka']['build_time']
        
        report += f"""
## Comparison

### File Size
- **Difference:** {abs(size_diff):.2f} MB ({'PyInstaller' if size_diff > 0 else 'Nuitka'} is larger)
- **Winner:** {'Nuitka' if size_diff > 0 else 'PyInstaller'} (smaller)

### Build Time
- **Difference:** {abs(time_diff):.2f} seconds ({'PyInstaller' if time_diff < 0 else 'Nuitka'} is faster)
- **Winner:** {'PyInstaller' if time_diff < 0 else 'Nuitka'} (faster)

## Recommendations

"""
        
        if size_diff > 50:
            report += "- **File Size:** Nuitka produces a significantly smaller executable\n"
        elif size_diff < -50:
            report += "- **File Size:** PyInstaller produces a significantly smaller executable\n"
        
        if abs(time_diff) > 60:
            faster = 'PyInstaller' if time_diff < 0 else 'Nuitka'
            report += f"- **Build Time:** {faster} builds much faster\n"
        
        report += "\n## Notes\n\n"
        report += "- Both executables should be tested to ensure all features work correctly\n"
        report += "- Startup time and runtime performance may differ\n"
        report += "- Consider your priorities: file size vs build time vs runtime performance\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Markdown report saved to: {output_path}")

def generate_html_report(results, output_path):
    """Generate an HTML comparison report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Helper function to format size
    def format_size(size):
        if isinstance(size, (int, float)):
            return f"{size:.2f}"
        return str(size)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Build Comparison Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #0d47a1;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #0d47a1;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .success {{
            color: #4caf50;
            font-weight: bold;
        }}
        .failed {{
            color: #f44336;
            font-weight: bold;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>Build Comparison Report</h1>
    <p class="timestamp">Generated: {timestamp}</p>
    
    <div class="section">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Tool</th>
                <th>Status</th>
                <th>Executable Size</th>
                <th>Build Time</th>
            </tr>
            <tr>
                <td>PyInstaller</td>
                <td class="{'success' if results['pyinstaller']['success'] else 'failed'}">
                    {'✓ Success' if results['pyinstaller']['success'] else '✗ Failed'}
                </td>
                <td>{format_size(results['pyinstaller'].get('size_mb', 'N/A'))} MB</td>
                <td>{results['pyinstaller'].get('build_time', 0):.2f}s</td>
            </tr>
            <tr>
                <td>Nuitka</td>
                <td class="{'success' if results['nuitka']['success'] else 'failed'}">
                    {'✓ Success' if results['nuitka']['success'] else '✗ Failed'}
                </td>
                <td>{format_size(results['nuitka'].get('size_mb', 'N/A'))} MB</td>
                <td>{results['nuitka'].get('build_time', 0):.2f}s</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Detailed Results</h2>
        <h3>PyInstaller</h3>
"""
    
    if results['pyinstaller']['success']:
        html += f"""
        <ul>
            <li><strong>Status:</strong> <span class="success">✓ Build Successful</span></li>
            <li><strong>Executable Path:</strong> <code>{results['pyinstaller']['exe_path']}</code></li>
            <li><strong>File Size:</strong> {results['pyinstaller']['size_mb']:.2f} MB</li>
            <li><strong>Build Time:</strong> {results['pyinstaller']['build_time']:.2f} seconds</li>
        </ul>
"""
    else:
        html += f"""
        <ul>
            <li><strong>Status:</strong> <span class="failed">✗ Build Failed</span></li>
            <li><strong>Error:</strong> {results['pyinstaller'].get('error', 'Unknown error')}</li>
            <li><strong>Build Time:</strong> {results['pyinstaller'].get('build_time', 0):.2f} seconds</li>
        </ul>
"""
    
    html += """
        <h3>Nuitka</h3>
"""
    
    if results['nuitka']['success']:
        html += f"""
        <ul>
            <li><strong>Status:</strong> <span class="success">✓ Build Successful</span></li>
            <li><strong>Executable Path:</strong> <code>{results['nuitka']['exe_path']}</code></li>
            <li><strong>File Size:</strong> {results['nuitka']['size_mb']:.2f} MB</li>
            <li><strong>Build Time:</strong> {results['nuitka']['build_time']:.2f} seconds</li>
        </ul>
"""
    else:
        html += f"""
        <ul>
            <li><strong>Status:</strong> <span class="failed">✗ Build Failed</span></li>
            <li><strong>Error:</strong> {results['nuitka'].get('error', 'Unknown error')}</li>
            <li><strong>Build Time:</strong> {results['nuitka'].get('build_time', 0):.2f} seconds</li>
        </ul>
"""
    
    if results['pyinstaller']['success'] and results['nuitka']['success']:
        size_diff = results['pyinstaller']['size_mb'] - results['nuitka']['size_mb']
        time_diff = results['pyinstaller']['build_time'] - results['nuitka']['build_time']
        
        html += f"""
    </div>
    
    <div class="section">
        <h2>Comparison</h2>
        <h3>File Size</h3>
        <ul>
            <li><strong>Difference:</strong> {abs(size_diff):.2f} MB ({'PyInstaller' if size_diff > 0 else 'Nuitka'} is larger)</li>
            <li><strong>Winner:</strong> {'Nuitka' if size_diff > 0 else 'PyInstaller'} (smaller)</li>
        </ul>
        <h3>Build Time</h3>
        <ul>
            <li><strong>Difference:</strong> {abs(time_diff):.2f} seconds ({'PyInstaller' if time_diff < 0 else 'Nuitka'} is faster)</li>
            <li><strong>Winner:</strong> {'PyInstaller' if time_diff < 0 else 'Nuitka'} (faster)</li>
        </ul>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML report saved to: {output_path}")

def main():
    """Main build and comparison function."""
    print("="*60)
    print("Dual Build System - PyInstaller & Nuitka")
    print("="*60)
    
    results = {
        'pyinstaller': {},
        'nuitka': {}
    }
    
    # Build with PyInstaller
    print("\n[1/2] Building with PyInstaller...")
    pyinstaller_success, pyinstaller_result = build_pyinstaller(clean=True)
    results['pyinstaller'] = pyinstaller_result
    
    # Build with Nuitka
    print("\n[2/2] Building with Nuitka...")
    nuitka_success, nuitka_result = build_nuitka(clean=True)
    results['nuitka'] = nuitka_result
    
    # Generate reports
    print("\n" + "="*60)
    print("Generating Comparison Reports...")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = project_root / 'build' / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Markdown report (always generated)
    md_report_path = reports_dir / f'comparison_report_{timestamp}.md'
    generate_markdown_report(results, md_report_path)
    
    # HTML report (optional, always generated)
    html_report_path = reports_dir / f'comparison_report_{timestamp}.html'
    generate_html_report(results, html_report_path)
    
    # Summary
    print("\n" + "="*60)
    print("Build Summary")
    print("="*60)
    print(f"PyInstaller: {'✓ Success' if pyinstaller_success else '✗ Failed'}")
    print(f"Nuitka: {'✓ Success' if nuitka_success else '✗ Failed'}")
    print(f"\nReports saved to: {reports_dir}")
    print(f"  - Markdown: {md_report_path.name}")
    print(f"  - HTML: {html_report_path.name}")
    
    return pyinstaller_success and nuitka_success

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Build executables with both PyInstaller and Nuitka')
    parser.add_argument('--html-only', action='store_true', help='Generate only HTML report')
    parser.add_argument('--md-only', action='store_true', help='Generate only Markdown report')
    args = parser.parse_args()
    
    success = main()
    sys.exit(0 if success else 1)

