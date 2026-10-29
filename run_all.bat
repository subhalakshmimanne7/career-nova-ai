@echo off
title Career Nova AI Launcher
echo ==================================================
echo   Launching Career Nova AI Full Stack Suite
echo ==================================================
start "Career Nova Backend" cmd /k "%~dp0run_backend.bat"
echo Waiting for backend initialization...
timeout /t 3 /nobreak >nul
start "Career Nova Frontend" cmd /k "%~dp0run_frontend.bat"
echo Done! Application is opening...
