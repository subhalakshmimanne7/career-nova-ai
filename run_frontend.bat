@echo off
title Career Nova AI - React Frontend
echo ==================================================
echo   Starting Career Nova AI - Vite + React Frontend
echo   Running on: http://localhost:5173
echo ==================================================
set PATH=C:\Program Files\nodejs;%PATH%
cd /d "%~dp0frontend"
call npm.cmd run dev
pause
