@echo off
cd /d "%~dp0"
echo ========================================
echo   🏈 アメフト戦術提案アプリ
echo ========================================
echo.
echo [1] 通常モード (同じWi-Fi用)
echo [2] 公開モード (外出先・ギガ用)
echo.
set /p choice="起動する番号を選んでください (1 or 2): "

if "%choice%"=="1" (
    "C:\Users\shuma\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run app.py --server.address 0.0.0.0
) else if "%choice%"=="2" (
    "C:\Users\shuma\AppData\Local\Programs\Python\Python314\python.exe" public_launch.py
) else (
    echo 無効な選択です。
    pause
)
