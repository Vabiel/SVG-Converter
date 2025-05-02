@echo off
setlocal EnableDelayedExpansion

:: Script to set up a virtual environment and run the SVG optimizer on Windows

:: Configuration
set VENV_DIR=venv
set PYTHON=python
set CONSOLE_SCRIPT=svg_optimizer_console.py
set PYQT5_SCRIPT=svg_optimizer_pyqt5.py
set REQUIREMENTS=lxml PyQt5 Pillow

:: Check if Python is installed
where %PYTHON% >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3 is not installed. Please install Python 3 from https://www.python.org/downloads/ and try again.
    pause
    exit /b 1
)

:: Check Python version (must be 3.x)
%PYTHON% --version | findstr /R "Python 3" >nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3 is required. Found incompatible version.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment in %VENV_DIR%...
    %PYTHON% -m venv %VENV_DIR%
    if !ERRORLEVEL! neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists in %VENV_DIR%.
)

:: Activate virtual environment
call %VENV_DIR%\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
for %%i in (%REQUIREMENTS%) do (
    pip install %%i
    if !ERRORLEVEL! neq 0 (
        echo Error: Failed to install %%i. Check your internet connection or pip version.
        call deactivate
        pause
        exit /b 1
    )
)
echo Dependencies installed successfully.

:: Check if scripts exist
set CONSOLE_EXISTS=0
set PYQT5_EXISTS=0
if exist "%CONSOLE_SCRIPT%" set CONSOLE_EXISTS=1
if exist "%PYQT5_SCRIPT%" set PYQT5_EXISTS=1
if %CONSOLE_EXISTS%==0 if %PYQT5_EXISTS%==0 (
    echo Error: Neither %CONSOLE_SCRIPT% nor %PYQT5_SCRIPT% found in the src directory.
    call deactivate
    pause
    exit /b 1
)

:: Prompt user to choose which script to run
echo Which SVG optimizer would you like to run?
if %CONSOLE_EXISTS%==1 (
    echo 1) Console-based optimizer (%CONSOLE_SCRIPT%)
)
if %PYQT5_EXISTS%==1 (
    echo 2) PyQt5-based GUI optimizer (%PYQT5_SCRIPT%)
)
echo Enter 1 or 2 (or press Enter to exit):
set /p choice=

if "!choice!"=="1" (
    if %CONSOLE_EXISTS%==1 (
        echo Running %CONSOLE_SCRIPT%...
        %PYTHON% %CONSOLE_SCRIPT% %*
    ) else (
        echo Error: %CONSOLE_SCRIPT% not found.
    )
) else if "!choice!"=="2" (
    if %PYQT5_EXISTS%==1 (
        echo Running %PYQT5_SCRIPT%...
        %PYTHON% %PYQT5_SCRIPT%
    ) else (
        echo Error: %PYQT5_SCRIPT% not found.
    )
) else (
    echo Exiting without running any script.
)

:: Deactivate virtual environment
call deactivate
pause
exit /b 0