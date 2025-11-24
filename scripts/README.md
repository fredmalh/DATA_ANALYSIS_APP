# Build Scripts

This directory contains scripts for building executables from the Data Analysis Application.

## Scripts

### `build_pyinstaller.py`
Builds an executable using PyInstaller.

**Usage:**
```bash
python scripts/build_pyinstaller.py
```

**Options:**
- `--no-clean` - Skip cleaning previous build artifacts

### `build_nuitka.py`
Builds an executable using Nuitka.

**Usage:**
```bash
python scripts/build_nuitka.py
```

**Options:**
- `--no-clean` - Skip cleaning previous build artifacts

### `build_all.py`
Builds executables with both PyInstaller and Nuitka, then generates comparison reports.

**Usage:**
```bash
python scripts/build_all.py
```

**Options:**
- `--html-only` - Generate only HTML report
- `--md-only` - Generate only Markdown report

## Output

- **PyInstaller builds:** `build/pyinstaller/dist/DataAnalysisApp.exe`
- **Nuitka builds:** `build/nuitka/dist/DataAnalysisApp.exe`
- **Comparison reports:** `build/reports/comparison_report_YYYYMMDD_HHMMSS.md` and `.html`

## Prerequisites

Install build dependencies:
```bash
pip install -r requirements-build.txt
```

