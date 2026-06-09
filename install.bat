@echo off
REM SSZ-HOW-TO-BEAM v1.0.0 Installation Script
REM For Windows

echo ==================================
echo SSZ-HOW-TO-BEAM v1.0.0 Installer
echo ==================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10 or higher.
    exit /b 1
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Found Python %PYTHON_VERSION%

REM Check if version is 3.10+
echo %PYTHON_VERSION% | findstr /B "3.1" >nul
if errorlevel 1 (
    echo %PYTHON_VERSION% | findstr /B "3.2" >nul
    if errorlevel 1 (
        echo Error: Python 3.10 or higher is required
        exit /b 1
    )
)

echo [ok] Python version check passed
echo.

REM Check for virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo Note: Not in a virtual environment.
    echo Recommended: Create a venv first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo.
    set /p CONTINUE="Continue anyway? [y/N] "
    if /I not "%CONTINUE%"=="y" exit /b 1
)

REM Installation mode
if "%1"=="--dev" (
    echo Installing in DEVELOPMENT mode...
    pip install -r requirements-dev.txt
    pip install -e .
    echo.
    echo [ok] Development installation complete
    echo   Includes: pytest, black, ruff, mypy, sphinx
) else if "%1"=="--all" (
    echo Installing with ALL optional dependencies...
    pip install -r requirements.txt
    pip install h5py sympy matplotlib
    pip install -e .
    echo.
    echo [ok] Full installation complete
    echo   Includes: h5py, sympy, matplotlib
) else (
    echo Installing CORE dependencies only...
    pip install -r requirements.txt
    pip install -e .
    echo.
    echo [ok] Core installation complete
    echo   For full features, run: install.bat --all
)

echo.
echo ==================================
echo Testing installation...
echo ==================================
echo.

REM Test import
python -c "import beam_ssz; print(f'Version: {beam_ssz.__version__}')"

if %errorlevel%==0 (
    echo.
    echo [ok] Installation successful!
    echo.
    echo Quick start:
    echo   python -c "import beam_ssz; print(beam_ssz.__version__)"
    echo   python -m pytest tests/ -q
    echo.
) else (
    echo.
    echo [x] Installation test failed
    exit /b 1
)
