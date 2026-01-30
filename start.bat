@echo off
echo =======================================
echo   Viktspårare - Weight Tracker
echo =======================================
echo.

REM Kontrollera om Python är installerat
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo FEL: Python är inte installerat eller finns inte i PATH!
    echo.
    echo Ladda ner Python från: https://www.python.org/downloads/
    echo VIKTIGT: Kryssa i "Add Python to PATH" vid installation!
    echo.
    pause
    exit /b 1
)

echo Python hittat! Startar Viktspåraren...
echo.

python weight_tracker_V1.py

if %errorlevel% neq 0 (
    echo.
    echo =======================================
    echo Ett fel uppstod!
    echo =======================================
    echo.
    echo Om du får felmeddelande om saknade moduler, kör:
    echo   pip install -r requirements.txt
    echo.
    pause
)
