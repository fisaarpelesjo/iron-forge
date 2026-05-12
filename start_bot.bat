@echo off
cd /d "%~dp0"

py -3 ironforge_banner.py
if "%ERRORLEVEL%"=="9009" (
  python ironforge_banner.py
)

echo Starting training bot...
echo(

py -3 telegram_poller.py
set "exit_code=%ERRORLEVEL%"
if "%exit_code%"=="9009" (
  python telegram_poller.py
  set "exit_code=%ERRORLEVEL%"
)

echo.
echo Bot stopped with exit code %exit_code%.
echo.

pause
exit /b %exit_code%
