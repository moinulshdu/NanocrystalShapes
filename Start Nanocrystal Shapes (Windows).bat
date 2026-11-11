@echo off
rem ------------------------------------------------------------------
rem  Starts Nanocrystal Shapes without a console window.
rem  Looks for Anaconda/Miniconda first, then the python.org install.
rem ------------------------------------------------------------------
setlocal
cd /d "%~dp0"
set "APP=%~dp0Nanocrystal Shapes.pyw"

for %%P in ("%ProgramData%\anaconda3" "%USERPROFILE%\anaconda3" "%LOCALAPPDATA%\anaconda3" "%ProgramData%\Anaconda3" "%ProgramData%\miniconda3" "%USERPROFILE%\miniconda3" "%LOCALAPPDATA%\miniconda3") do (
    if exist "%%~P\pythonw.exe" (
        set "PATH=%%~P;%%~P\Library\bin;%%~P\Scripts;%PATH%"
        start "" "%%~P\pythonw.exe" "%APP%" %*
        exit /b 0
    )
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "%APP%" %*
    exit /b 0
)

for /f "delims=" %%W in ('where pythonw 2^>nul') do (
    echo %%W | find /i "WindowsApps" >nul || (
        start "" "%%W" "%APP%" %*
        exit /b 0
    )
)

echo.
echo  Python was not found on this computer.
echo.
echo  Please install Python 3 from https://www.python.org/downloads/
echo  and tick "Add python.exe to PATH" during installation.
echo  Then double-click this file again.
echo.
pause
