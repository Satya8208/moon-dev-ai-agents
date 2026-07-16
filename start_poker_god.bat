@echo off
echo.
echo ============================================================
echo   ♠♥ POKER GOD DASHBOARD ♦♣
echo   GTO + Exploitative Play | Cash ^& Tournaments
echo   Built with love by Moon Dev
echo ============================================================
echo.
echo   Starting server on http://localhost:8001
echo.

cd /d "%~dp0src\agents\poker\web_dashboard"
python run_dashboard.py
pause
