@echo off
REM Bennett-Kew Weekly Report - Scheduled Friday 8:00 AM
REM Set up in Windows Task Scheduler:
REM   Trigger: Weekly, Friday at 8:00 AM
REM   Action: Start program -> this batch file
REM   Conditions: Start only if network available

cd /d C:\Users\Adam\DEV\projects\fsi-weekly-report\bennett-kew-report-automate

REM Activate venv if exists, otherwise use system Python
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

set PYTHONUTF8=1
python run.py 2>&1 >> output\scheduler_log.txt

echo %DATE% %TIME% - Report generation complete >> output\scheduler_log.txt
