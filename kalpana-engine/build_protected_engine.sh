#!/bin/bash
set -e

echo "=========================================================="
echo "⚡ Building Protected Kalpanā Native Core Engine (Cython)"
echo "=========================================================="

# 1. Build C-extension .so / .pyd binary from core.py
echo "1. Cythonizing core.py into native machine code..."
python3 setup_cython.py build_ext --inplace

# 2. Clean up C source files to avoid leaving plain text C code
echo "2. Cleaning intermediate C source files..."
rm -f core.c

# 3. Verify native binary module import
echo "3. Verifying native binary module import..."
python3 -c "import core; print('✅ Successfully imported native module:', core.__file__)"

# 4. Optional: Run PyInstaller to bundle executable
if command -v pyinstaller &> /dev/null; then
    echo "4. Bundling protected executable with PyInstaller..."
    pyinstaller kalpana-engine-mac.spec --clean --noconfirm
    echo "✅ Executable build completed in dist/kalpana-engine-mac"
else
    echo "⚠️ PyInstaller not found in environment, skipping PyInstaller bundle step."
fi

echo "=========================================================="
echo "🔒 RIF Engine Core is now compiled to Native Machine Code!"
echo "=========================================================="
