@echo off
setlocal

REM Check for Malmo
if "%MALMO_DIR%"=="" (
    if exist "C:\MalmoPlatform\Malmo-0.37.0-Windows-64bit_withBoost_Python3.7" (
        set "MALMO_DIR=C:\MalmoPlatform\Malmo-0.37.0-Windows-64bit_withBoost_Python3.7"
        echo [INFO] Found Malmo at %MALMO_DIR%
    ) else (
        echo [ERROR] Please set MALMO_DIR to your Malmo installation path.
        pause
        exit /b 1
    )
)

echo [INFO] Launching Minecraft Client from %MALMO_DIR%...

REM Try to find launchClient.bat
if exist "%MALMO_DIR%\launchClient.bat" (
    cd /d "%MALMO_DIR%"
    call launchClient.bat
) else if exist "%MALMO_DIR%\Minecraft\launchClient.bat" (
    cd /d "%MALMO_DIR%\Minecraft"
    call launchClient.bat
) else (
    echo [ERROR] Could not find launchClient.bat in %MALMO_DIR% or %MALMO_DIR%\Minecraft
    pause
    exit /b 1
)

endlocal
