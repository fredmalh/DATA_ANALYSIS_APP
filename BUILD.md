# Building Executables

This document explains how to build executable files for the Data Analysis Application.

## Quick Start

1. **Install build dependencies:**
   ```bash
   pip install -r requirements-build.txt
   ```

2. **Build both executables and generate comparison:**
   ```bash
   python scripts/build_all.py
   ```

3. **Find your executables:**
   - PyInstaller: `build/pyinstaller/dist/DataAnalysisApp.exe`
   - Nuitka: `build/nuitka/dist/DataAnalysisApp.exe`
   - Reports: `build/reports/comparison_report_*.md` and `.html`

## Individual Builds

### Build with PyInstaller only:
```bash
python scripts/build_pyinstaller.py
```

### Build with Nuitka only:
```bash
python scripts/build_nuitka.py
```

## Build Options

### PyInstaller
- **Configuration:** `build_configs/pyinstaller.spec`
- **Output:** Single executable file
- **Console:** Disabled (no console window)
- **Icon:** Can be added in the spec file

### Nuitka
- **Configuration:** Command-line options in `scripts/build_nuitka.py`
- **Output:** Single executable file
- **Console:** Disabled (no console window)
- **Plugins:** PyQt6 plugin enabled

## Comparison Reports

The `build_all.py` script automatically generates comparison reports in both Markdown and HTML formats.

**Report includes:**
- Build status for each tool
- File sizes
- Build times
- Comparison and recommendations

## Troubleshooting

### PyInstaller Issues

**Missing modules:**
- Add them to `hiddenimports` in `build_configs/pyinstaller.spec`

**Large file size:**
- This is normal for PyInstaller (typically 200-300 MB)
- Consider using `--onedir` instead of `--onefile` for faster startup

### Nuitka Issues

**Build fails:**
- Ensure you have a C++ compiler installed (Visual Studio on Windows)
- Check that all dependencies are installed

**Missing modules:**
- Add them to `--include-module` in `scripts/build_nuitka.py`

### General Issues

**Antivirus flags executable:**
- This is common with PyInstaller/Nuitka executables
- You may need to whitelist the build directory
- Consider code signing for distribution

**Executable doesn't run:**
- Check that all dependencies are included
- Test in a clean environment
- Check Windows Event Viewer for errors

## File Sizes

Expected file sizes:
- **PyInstaller:** ~200-300 MB
- **Nuitka:** ~150-250 MB

These sizes are normal due to bundled Python runtime and dependencies (pandas, numpy, matplotlib, PyQt6, etc.).

## Performance

- **Startup time:** 2-5 seconds (first launch may be slower)
- **Runtime:** Should be similar to running from source
- **Memory:** Similar to running from source

## Distribution

When distributing the executable:
1. Test thoroughly on a clean system
2. Consider code signing (Windows)
3. Provide clear installation instructions
4. Note system requirements (Windows 10+, etc.)

