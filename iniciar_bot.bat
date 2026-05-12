@echo off
cd /d "%~dp0"

echo.
echo  III  RRRR   OOO  N   N  FFFFF  OOO  RRRR   GGG  EEEEE
echo   I   R   R O   O NN  N  F     O   O R   R G     E
echo   I   RRRR  O   O N N N  FFF   O   O RRRR  G  GG EEEE
echo   I   R  R  O   O N  NN  F     O   O R  R  G   G E
echo  III  R   R  OOO  N   N  F      OOO  R   R  GGG  EEEEE
echo.
echo Starting training bot...
echo.

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
