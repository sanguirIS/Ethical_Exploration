@echo off
echo Optimizing server performance...

:: Stop unnecessary services
echo Stopping unnecessary services...
net stop "Windows Update"
net stop "Superfetch"
net stop "Windows Search"
:: Add more services as needed

:: Clear temporary files
echo Clearing temporary files...
del /s /q %TEMP%\*
del /s /q C:\Windows\Temp\*

:: Clear DNS cache
echo Clearing DNS cache...
ipconfig /flushdns

:: Optimize network settings
echo Optimizing network settings...
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
netsh int tcp set global dca=enabled
netsh int tcp set global netdma=enabled

:: Defragment hard drive (Optional, time-consuming)
:: echo Defragmenting hard drive...
:: defrag C: /H /U /V

:: Free up memory (Clear Standby List)
echo Freeing up memory...
powershell.exe -command "Clear-DnsClientCache"
powershell.exe -command "[void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Hibernate, $false, $false)"

:: Display memory status
echo Displaying memory status...
systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"

:: Restart server (Optional)
:: echo Restarting server...
:: shutdown /r /t 0

echo Optimization complete.
pause
