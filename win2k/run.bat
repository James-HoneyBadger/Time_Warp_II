@echo off
REM  Time Warp II -- Retro Edition
REM  Launcher for Windows 2000 / Python 2.7
REM  =========================================
REM
REM  Make sure Python 2.7 is installed and in your PATH.
REM  Download from: https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
REM

title Time Warp II -- Retro Edition

REM Try pythonw first (no console window)
where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
    start "" pythonw "%~dp0TimeWarpII.pyw"
    goto :eof
)

REM Fallback: try python
where python >nul 2>&1
if %ERRORLEVEL%==0 (
    python "%~dp0TimeWarpII.pyw"
    goto :eof
)

REM Last resort: check common install paths
if exist "C:\Python27\pythonw.exe" (
    start "" "C:\Python27\pythonw.exe" "%~dp0TimeWarpII.pyw"
    goto :eof
)

if exist "C:\Python27\python.exe" (
    "C:\Python27\python.exe" "%~dp0TimeWarpII.pyw"
    goto :eof
)

echo.
echo  ERROR: Python 2.7 not found!
echo.
echo  Please install Python 2.7.8 from:
echo  https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
echo.
echo  After installing, make sure to add Python to your PATH,
echo  or install to the default location (C:\Python27).
echo.
pause
