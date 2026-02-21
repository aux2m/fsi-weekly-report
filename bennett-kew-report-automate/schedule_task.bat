@echo off
REM ============================================================
REM  Bennett-Kew Weekly Report - Scheduled Automation
REM  Runs every Friday at 9:30 AM via Windows Task Scheduler
REM  Backend: API (Anthropic API)
REM ============================================================

set PYTHONUTF8=1
set PROJECT_DIR=C:\Users\Adam\DEV\projects\fsi-weekly-report\bennett-kew-report-automate
set LOG_DIR=%PROJECT_DIR%\output\logs
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\run_%TIMESTAMP%.log

REM Create log directory if needed
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%date% %time%] Starting weekly report generation >> "%LOG_FILE%"
echo ================================================== >> "%LOG_FILE%"

cd /d "%PROJECT_DIR%"

C:\Python314\python.exe run.py --backend api >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] SUCCESS - Report generated >> "%LOG_FILE%"
) else (
    echo [%date% %time%] FAILED - Exit code: %ERRORLEVEL% >> "%LOG_FILE%"
)

echo ================================================== >> "%LOG_FILE%"
echo [%date% %time%] Done >> "%LOG_FILE%"
