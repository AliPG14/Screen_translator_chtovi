@echo off
echo ============================================
echo   Douyin Screen Translator - Cai dat
echo ============================================
echo.
echo Dang kiem tra Python...
python --version 2>NUL
if errorlevel 1 (
    echo [LOI] Khong tim thay Python! Hay tai Python 3.8+ tai https://python.org
    pause
    exit /b 1
)
echo [OK] Tim thay Python.
echo.
echo Dang cap nhat pip...
python -m pip install --upgrade pip
echo.
echo Dang cai dat cac thu vien...
pip install -r requirements.txt
echo.
echo ============================================
echo   Cai dat hoan tat!
echo   Chay: python main.py
echo ============================================
pause
