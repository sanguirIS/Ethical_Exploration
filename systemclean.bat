@echo off
echo ============================================
echo Running System Cleanup
echo ============================================

:: Step 1: Update Windows Defender
echo Updating Windows Defender...
"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -SignatureUpdate
echo Done.

:: Step 2: Run a Quick Scan with Windows Defender
echo Running Quick Scan with Windows Defender...
"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -Scan -ScanType 1
echo Done.

:: Step 3: Clean Temporary Files
echo Cleaning Temporary Files...
del /s /f /q %temp%\*
del /s /f /q C:\Windows\Temp\*
echo Done.

:: Step 4: Clean some common registry paths
echo Cleaning Registry...

:: Backing up the registry first
reg export HKCU\Software\Microsoft\Windows\CurrentVersion\Run run_backup.reg

:: Deleting unwanted startup items
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "unwanted_program" /f

:: You can add more registry cleaning commands as needed
echo Done.

echo ============================================
echo System Cleanup Complete
echo ============================================
pause
