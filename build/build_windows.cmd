@echo off
REM Build FoodLog for Windows

echo Building FoodLog for Windows...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install PyInstaller if needed
pip install pyinstaller

REM Create dist directory
if not exist "dist\FoodLog_Windows" mkdir dist\FoodLog_Windows

REM Run PyInstaller
pyinstaller --onedir ^
    --windowed ^
    --distpath=dist\FoodLog_Windows ^
    --buildpath=build\temp_windows ^
    build\foodlog.spec

REM Copy README and any documentation
REM copy README.md dist\FoodLog_Windows\
REM copy SPEC.md dist\FoodLog_Windows\

echo Build complete! Binary at: dist\FoodLog_Windows\foodlog_win\
echo To run: dist\FoodLog_Windows\foodlog_win\foodlog_win.exe
