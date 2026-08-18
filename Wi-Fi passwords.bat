@echo off
:: Ethical Exploration - Windows Wi-Fi Profile & Key Retrieval Utility
:: License: GNU General Public License v3.0 (GPL-3.0)

setlocal enabledelayedexpansion

:: Elevate to Administrator if needed
:check_permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo [*] Requesting administrative privileges...
    goto uac_prompt
) else (
    goto got_admin
)

:uac_prompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set "params=%*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:got_admin
    pushd "%CD%"
    CD /D "%~dp0"

echo =========================================================
echo    Ethical Exploration - Wi-Fi Profile & Password Audit  
echo =========================================================
echo.

set "OUTPUT_FILE=wifi_passwords_export.txt"
echo Wi-Fi Profiles and Passwords > "%OUTPUT_FILE%"
echo Generated on %DATE% %TIME% >> "%OUTPUT_FILE%"
echo ========================================================= >> "%OUTPUT_FILE%"

echo [*] Querying saved wireless profiles...
echo.

for /f "tokens=2 delims=:" %%i in ('netsh wlan show profiles ^| findstr /C:"All User Profile"') do (
    set "SSID=%%i"
    set "SSID=!SSID:~1!"
    
    echo ---------------------------------------------------------
    echo SSID / Network Name: !SSID!
    echo --------------------------------------------------------- >> "%OUTPUT_FILE%"
    echo SSID: !SSID! >> "%OUTPUT_FILE%"
    
    for /f "tokens=2 delims=:" %%k in ('netsh wlan show profile name^="!SSID!" key^=clear ^| findstr /C:"Key Content"') do (
        set "KEY=%%k"
        set "KEY=!KEY:~1!"
        echo Password / Key    : !KEY!
        echo Password: !KEY! >> "%OUTPUT_FILE%"
    )
    echo.
    echo. >> "%OUTPUT_FILE%"
)

echo =========================================================
echo [*] Wi-Fi password extraction complete.
echo [*] Results exported to: %OUTPUT_FILE%
echo =========================================================
pause
