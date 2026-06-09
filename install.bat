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

REM Check for virtual environment directory, create one if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo [ok] Virtual environment created in .venv\
    echo.
)

REM ALWAYS use venv paths
set "VENV_PIP=.venv\Scripts\pip"
set "VENV_PYTHON=.venv\Scripts\python"

REM Upgrade pip in venv
echo Upgrading pip...
%VENV_PIP% install --upgrade pip

REM Installation mode
if "%1"=="--dev" (
    echo.
    echo Installing in DEVELOPMENT mode...
    %VENV_PIP% install -r requirements-dev.txt
    %VENV_PIP% install -e .
    echo.
    echo [ok] Development installation complete
    echo   Includes: pytest, black, ruff, mypy, sphinx
) else if "%1"=="--all" (
    echo.
    echo Installing with ALL optional dependencies...
    %VENV_PIP% install -r requirements.txt
    %VENV_PIP% install h5py sympy matplotlib
    %VENV_PIP% install -e .
    echo.
    echo [ok] Full installation complete
    echo   Includes: h5py, sympy, matplotlib
) else (
    echo.
    echo Installing CORE dependencies only...
    %VENV_PIP% install -r requirements.txt
    %VENV_PIP% install -e .
    echo.
    echo [ok] Core installation complete
    echo   For full features, run: install.bat --all
)

echo.
echo ==================================
echo Testing installation...
echo ==================================
echo.

REM Test import using venv python
%VENV_PYTHON% -c "import beam_ssz; print(f'Version: {beam_ssz.__version__}')"

if %errorlevel%==0 (
    echo.
    echo [ok] Installation successful!
    echo.
    echo Quick start:
    echo   .venv\Scripts\activate
    echo   python -c "import beam_ssz; print(beam_ssz.__version__)"
    echo   python run_complete_validation.py
    echo.
) else (
    echo.
    echo [x] Installation test failed
    exit /b 1
)
