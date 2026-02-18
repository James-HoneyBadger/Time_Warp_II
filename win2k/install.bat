@echo off
REM  Time Warp II -- Retro Edition  --  Install Helper
REM  ===================================================
REM  This script verifies that Python 2.7 is installed
REM  and that Tkinter is available.
REM

title Time Warp II -- Install Check

echo.
echo  ============================================
echo   Time Warp II -- Retro Edition
echo   Install Verification
echo  ============================================
echo.

REM Check Python
python -c "import sys; print('  Python version: %%s' %% sys.version)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo  [FAIL] Python is not installed or not in PATH.
    echo.
    echo  Download Python 2.7.8 from:
    echo  https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
    echo.
    echo  During installation, select "Add python.exe to Path".
    echo.
    goto :done
)
echo  [OK]   Python found.

REM Check Tkinter
python -c "import Tkinter; print('  Tkinter version: %%s' %% Tkinter.TkVersion)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo  [FAIL] Tkinter is not available.
    echo         Reinstall Python 2.7 with Tcl/Tk support enabled.
    goto :done
)
echo  [OK]   Tkinter found.

REM Check ScrolledText
python -c "import ScrolledText; print('  ScrolledText: OK')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo  [WARN] ScrolledText module missing (should be in stdlib).
) else (
    echo  [OK]   ScrolledText found.
)

echo.
echo  ============================================
echo   All checks passed!
echo   Run "run.bat" to start Time Warp II.
echo  ============================================

:done
echo.
pause
