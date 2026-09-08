@echo off
setlocal
cd /d "%~dp0"
echo.
echo  MINNIONISE LOCAL BRIDGE
echo  =======================
echo.
echo  1. Desktop only
 echo 2. Desktop + iPhone/iPad QR pairing
 echo.
set /p choice=Choose 1 or 2: 
if "%choice%"=="2" (
  py -3 server.py --lan || python server.py --lan
) else (
  py -3 server.py || python server.py
)
pause
