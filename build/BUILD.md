# Building FoodLog

## Prerequisites

- Python 3.13
- pip / uv package manager
- PyInstaller

## Linux Build

```bash
cd /path/to/foodlog
bash build/build_linux.sh
```

The resulting binary will be at: `dist/FoodLog_Linux/foodlog_linux/foodlog_linux`

Run with:
```bash
./dist/FoodLog_Linux/foodlog_linux/foodlog_linux
```

## Windows Build

Run on Windows with:
```cmd
cd C:\path\to\foodlog
build\build_windows.cmd
```

The resulting binary will be at: `dist\FoodLog_Windows\foodlog_win\foodlog_win.exe`

Run with:
```cmd
dist\FoodLog_Windows\foodlog_win\foodlog_win.exe
```

## Cross-Platform Notes

- **Database Portability:** Both executables share the same `foodlog.db` file 
  format, allowing the same database to be used on Windows and Linux.
- **Path Resolution:** The app locates its own folder at runtime, enabling 
  thumb-drive portability. Never hardcode absolute paths.
- **Icon Files:** The `--icon` argument in PyInstaller points to 
  `build/foodlog.ico`. If the icon is missing, remove that argument.

## Directory Layout After Build

```
FoodLog/
  ├── foodlog_win.exe  (Windows)
  ├── foodlog_linux    (Linux)
  ├── foodlog.db       (Shared database)
  └── ... (other assets as needed)
```

## Troubleshooting

If PyInstaller build fails:
1. Ensure virtual environment is activated
2. Run `pip install --upgrade pyinstaller`
3. Check that all dependencies are installed: `pip install -r requirements.txt`
4. Verify Python 3.13 is in use: `python --version`
