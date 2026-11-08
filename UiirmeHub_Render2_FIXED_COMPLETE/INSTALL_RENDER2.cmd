@echo off
chcp 65001 >nul
title UiirmeHub Render2 Installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_RENDER2.ps1"
echo.
pause
