@echo off
:: Ethical Exploration - Microsoft Store Application Installer Utility
:: License: GNU General Public License v3.0 (GPL-3.0)

setlocal enabledelayedexpansion

echo =========================================================
echo    Ethical Exploration - Microsoft Store App Installer   
echo =========================================================
echo.

set "appID=%~1"
if "%appID%"=="" (
    set /p "appID=Enter Microsoft Store Product ID or Package Name: "
)

if "%appID%"=="" (
    echo [!] Error: No App ID provided. Exiting.
    pause
    exit /b 1
)

echo.
echo [*] Target App ID: %appID%
echo [*] Checking Microsoft Store AppX registration...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$store = Get-AppxPackage -AllUsers -Name Microsoft.WindowsStore; if ($store) { Add-AppxPackage -DisableDevelopmentMode -Register ($store.InstallLocation + '\AppXManifest.xml') -ErrorAction SilentlyContinue; Write-Host '[+] Windows Store component verified.' } else { Write-Warning 'Microsoft.WindowsStore package not found.' }"

echo [*] Launching Store product page for: %appID%
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process 'ms-windows-store://pdp/?productid=%appID%'"

echo [*] Waiting for Store interface to initialize...
timeout /t 5 >nul

echo [*] Checking installation state...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$installed = Get-AppxPackage -AllUsers | Where-Object { $_.Name -like '*%appID%*' -or $_.PackageFamilyName -like '*%appID%*' }; if ($installed) { Write-Host '[+] Application is already installed:' $installed.Name } else { Write-Host '[*] Triggering direct install protocol...'; Start-Process 'ms-windows-store://install/?appid=%appID%' }"

echo.
echo =========================================================
echo [*] Installation workflow complete.
echo =========================================================
pause
