@echo off
cd /d "%~dp0"

py -3 start_bot.py
set "exit_code=%ERRORLEVEL%"
if "%exit_code%"=="9009" (
  python start_bot.py
  set "exit_code=%ERRORLEVEL%"
)

echo.
echo Bot encerrado com codigo de saida %exit_code%.
echo.

pause
exit /b %exit_code%
