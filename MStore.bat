@echo off
echo Installing application from Microsoft Store...
set "appID=Your_App_ID_Here"

powershell -Command "Add-AppxPackage -DisableDevelopmentMode -Register ((Get-AppxPackage -AllUsers -Name Microsoft.WindowsStore).InstallLocation + '\AppXManifest.xml')"
powershell -Command "Start-Process ms-windows-store://pdp/?productid=%appID%"

echo Waiting for the Store to open...
timeout /t 10 >nul

echo Attempting to install the application...
powershell -Command "Get-AppxPackage -AllUsers -Name %appID% -ErrorAction SilentlyContinue | Out-Null; if ($?) { echo 'App is already installed.'; } else { & explorer 'ms-windows-store://install/?appid=%appID%' }"

echo Installation script has finished.
pause
