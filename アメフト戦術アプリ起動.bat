@echo off
cd /d "%~dp0"
echo ========================================
echo   アメフト戦術提案アプリを起動中...
echo ========================================
echo.
"C:\Users\shuma\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run app.py --server.address 0.0.0.0
pause
