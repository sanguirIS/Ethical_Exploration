@echo off
:: Ethical Exploration - Server Performance & Network Optimization Utility
:: License: GNU General Public License v3.0 (GPL-3.0)

setlocal enabledelayedexpansion

echo =========================================================
echo    Ethical Exploration - Server Performance Optimizer   
echo =========================================================
echo.

:: Verify Administrator Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Warning: Please run this script as Administrator for full optimization.
    echo.
)

:: 1. Stop background telemetry and indexing services if desired
echo [*] Managing performance-heavy background services...
net stop "Windows Search" >nul 2>&1
net stop "SysMain" >nul 2>&1

:: 2. Clean temporary file caches
echo [*] Purging temporary files and cache...
if exist "%TEMP%" (
    del /s /f /q "%TEMP%\*" >nul 2>&1
    for /d %%p in ("%TEMP%\*") do rmdir /s /q "%%p" >nul 2>&1
)
if exist "C:\Windows\Temp" (
    del /s /f /q "C:\Windows\Temp\*" >nul 2>&1
    for /d %%p in ("C:\Windows\Temp\*") do rmdir /s /q "%%p" >nul 2>&1
)

:: 3. Flush DNS Cache
echo [*] Flushing DNS resolver cache...
ipconfig /flushdns >nul 2>&1
powershell -NoProfile -Command "Clear-DnsClientCache" >nul 2>&1

:: 4. Optimize TCP/IP Network Stack
echo [*] Optimizing network TCP window and auto-tuning...
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global chimney=enabled >nul 2>&1
netsh int tcp set global dca=enabled >nul 2>&1
netsh int tcp set global netdma=enabled >nul 2>&1

:: 5. Free System Memory & Trim Process Working Sets (Safe GC & Working Set Reduction)
echo [*] Reclaiming inactive memory and trimming working sets...
powershell -NoProfile -Command ^
    "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers(); Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }" >nul 2>&1

:: 6. Display Memory & Resource Summary
echo.
echo =========================================================
echo MEMORY & RESOURCE STATUS:
echo =========================================================
systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"
powershell -NoProfile -Command ^
    "$os = Get-CimInstance Win32_OperatingSystem; Write-Host ('Free Physical Memory : ' + [math]::Round($os.FreePhysicalMemory / 1024, 2) + ' MB / ' + [math]::Round($os.TotalVisibleMemorySize / 1024, 2) + ' MB')"

echo.
echo [!] Optimization completed successfully.
echo =========================================================
pause
