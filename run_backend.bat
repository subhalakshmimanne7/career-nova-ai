@echo off
title Career Nova AI - Backend Server
echo ==================================================
echo   Starting Career Nova AI - Flask REST API Backend
echo   Running on: http://127.0.0.1:5000
echo ==================================================
cd /d "%~dp0backend"
py app.py
pause
