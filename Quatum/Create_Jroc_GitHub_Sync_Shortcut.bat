@echo off
title Jroc Ai Desktop OS - Visual GitHub Sync
set "TARGET_DIR=C:\J-roc-AI\JrocAiDesktopOS\layer-04-execution-tools"
set "SCRIPT_NAME=github_visual_sync.py"
set "DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\Jroc_Ai_GitHub_Sync.bat"

if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

if exist "%~dp0%SCRIPT_NAME%" (
    copy /Y "%~dp0%SCRIPT_NAME%" "%TARGET_DIR%\%SCRIPT_NAME%" >nul
)

(
echo @echo off
echo cd /d "%TARGET_DIR%"
echo start "" pythonw "%SCRIPT_NAME%"
) > "%DESKTOP_SHORTCUT%"

if exist "%TARGET_DIR%\%SCRIPT_NAME%" (
    cd /d "%TARGET_DIR%"
    start "" pythonw "%SCRIPT_NAME%"
) else (
    echo [NOTICE] Place github_visual_sync.py inside:
    echo %TARGET_DIR%
    echo Then double-click Jroc_Ai_GitHub_Sync.bat on your Desktop.
    pause
)
